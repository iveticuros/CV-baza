import csv
import io
from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..constants import ROLE_COMPANY, ROLE_STUDENT
from ..database import get_db
from ..models.access_grant import AccessGrant
from ..models.audit_log import AuditLog
from ..models.company_profile import CompanyProfile
from ..models.company_student_access import CompanyStudentAccess
from ..models.deletion_request import DeletionRequest
from ..models.edit_grant import EditGrant
from ..models.fakultet import Fakultet
from ..models.refresh_token import RefreshToken
from ..models.student import Student

from ..models.user import User
from ..schemas.user import UserCreateAdmin, UserPublic, UserRole, UserUpdate
from ..services import audit as audit_service
from ..services import email as email_service
from ..request_context import client_ip_ctx, request_id_ctx
from ..utils.auth import CurrentAdmin
from ..utils.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])


class AccessGrantCreate(BaseModel):
    company_user_id: int
    max_cv_count: int = Field(..., ge=1, le=100000)
    valid_from: date
    valid_until: date


class AssignStudentsBody(BaseModel):
    student_ids: List[int]


class EditGrantBody(BaseModel):
    reason: Optional[str] = None


class DeletionProcessBody(BaseModel):
    approve: bool
    note: Optional[str] = Field(None, max_length=500)


def _revoke_refresh_all(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).update({"revoked": True})


@router.get("/users", response_model=List[UserPublic])
def list_users(
    _admin: CurrentAdmin,
    db: Session = Depends(get_db),
    role: Optional[str] = None,
    pending_approval: Optional[bool] = None,
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if pending_approval is True:
        q = q.filter(User.admin_approved == False, User.role == ROLE_STUDENT)  # noqa: E712
    return q.order_by(User.id).all()


@router.post("/users", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    body: UserCreateAdmin,
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    if body.role not in (UserRole.company, UserRole.admin):
        raise HTTPException(status_code=400, detail="Možete kreirati samo company ili admin ulogu.")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email je zauzet.")
    try:
        hashed = get_password_hash(body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    u = User(
        name=body.name,
        email=body.email,
        role=body.role.value,
        hashed_password=hashed,
        is_active=True,
        email_verified=True,
        admin_approved=True,
        failed_login_attempts=0,
    )
    db.add(u)
    db.flush()
    if body.role == UserRole.company:
        db.add(
            CompanyProfile(
                user_id=u.id,
                company_name=body.name,
                contact_person=body.name,
            )
        )
    db.commit()
    audit_service.write_audit(
        db,
        user_id=admin.id,
        action="admin_create_user",
        resource_type="user",
        resource_id=u.id,
        ip_address=client_ip_ctx.get(),
        request_id=request_id_ctx.get(),
        details={"role": body.role.value},
    )
    db.commit()
    return UserPublic.model_validate(u)


@router.put("/users/{user_id}", response_model=UserPublic)
def update_user_admin(
    user_id: int,
    body: UserUpdate,
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    if body.name is not None:
        u.name = body.name
    if body.email is not None:
        u.email = body.email
    if body.role is not None:
        u.role = body.role.value
    if body.is_active is not None:
        u.is_active = body.is_active
    if body.email_verified is not None:
        u.email_verified = body.email_verified
    if body.admin_approved is not None:
        u.admin_approved = body.admin_approved
    if body.password is not None:
        try:
            u.hashed_password = get_password_hash(body.password)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        _revoke_refresh_all(db, u.id)
    db.commit()
    return UserPublic.model_validate(u)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_admin(user_id: int, admin: CurrentAdmin, db: Session = Depends(get_db)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Ne možete obrisati sopstveni nalog.")
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    db.delete(u)
    db.commit()
    return None


@router.post("/users/{user_id}/approve-student", response_model=UserPublic)
async def approve_student(user_id: int, admin: CurrentAdmin, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id, User.role == ROLE_STUDENT).first()
    if not u:
        raise HTTPException(status_code=404, detail="Student nije pronađen.")
    u.admin_approved = True
    db.commit()
    try:
        await email_service.send_approval_email(u.email)
    except Exception:
        pass
    audit_service.write_audit(
        db,
        user_id=admin.id,
        action="admin_approve_student",
        resource_type="user",
        resource_id=u.id,
        ip_address=client_ip_ctx.get(),
        request_id=request_id_ctx.get(),
    )
    db.commit()
    return UserPublic.model_validate(u)


@router.post("/access-grants", response_model=dict)
def create_access_grant(
    body: AccessGrantCreate,
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    company_user = db.query(User).filter(User.id == body.company_user_id, User.role == ROLE_COMPANY).first()
    if not company_user:
        raise HTTPException(status_code=400, detail="Neispravan company korisnik.")
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == company_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Profil kompanije ne postoji.")
    if body.valid_until < body.valid_from:
        raise HTTPException(status_code=400, detail="Datumi pristupa nisu ispravni.")
    g = AccessGrant(
        company_profile_id=profile.id,
        max_cv_count=body.max_cv_count,
        valid_from=body.valid_from,
        valid_until=body.valid_until,
        used_cv_count=0,
        granted_by_user_id=admin.id,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return {"id": g.id}


class AccessGrantUpdate(BaseModel):
    max_cv_count: Optional[int] = Field(None, ge=1, le=100000)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


@router.put("/access-grants/{grant_id}", response_model=dict)
def update_access_grant(
    grant_id: int,
    body: AccessGrantUpdate,
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    g = db.query(AccessGrant).filter(AccessGrant.id == grant_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grant nije pronađen.")
    if body.max_cv_count is not None:
        g.max_cv_count = body.max_cv_count
    if body.valid_from is not None:
        g.valid_from = body.valid_from
    if body.valid_until is not None:
        g.valid_until = body.valid_until
    vf = g.valid_from
    vu = g.valid_until
    if vf and vu and vu < vf:
        raise HTTPException(status_code=400, detail="Datumi pristupa nisu ispravni.")
    db.commit()
    return {"id": g.id, "ok": True}


@router.post("/access-grants/{grant_id}/revoke")
def revoke_grant(grant_id: int, admin: CurrentAdmin, db: Session = Depends(get_db)):
    g = db.query(AccessGrant).filter(AccessGrant.id == grant_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grant nije pronađen.")
    g.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}


@router.post("/access-grants/{grant_id}/students")
def assign_students_to_grant(
    grant_id: int,
    body: AssignStudentsBody,
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    g = db.query(AccessGrant).filter(AccessGrant.id == grant_id, AccessGrant.revoked_at.is_(None)).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grant nije pronađen.")
    current = g.used_cv_count or 0
    pending_ids: List[int] = []
    for sid in body.student_ids:
        st = db.query(Student).filter(Student.id == sid).first()
        if not st:
            continue
        exists = (
            db.query(CompanyStudentAccess)
            .filter(
                CompanyStudentAccess.access_grant_id == grant_id,
                CompanyStudentAccess.student_id == sid,
            )
            .first()
        )
        if exists:
            continue
        pending_ids.append(sid)
    if current + len(pending_ids) > g.max_cv_count:
        raise HTTPException(status_code=400, detail="Prekoračen je maksimalan broj dodeljenih CV-ova.")
    for sid in pending_ids:
        db.add(
            CompanyStudentAccess(
                access_grant_id=grant_id,
                student_id=sid,
                granted_by_user_id=admin.id,
            )
        )
    g.used_cv_count = current + len(pending_ids)
    db.commit()
    return {"ok": True, "used_cv_count": g.used_cv_count}


@router.delete("/access-grants/{grant_id}/students/{student_id}")
def unassign_student(
    grant_id: int,
    student_id: int,
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    row = (
        db.query(CompanyStudentAccess)
        .filter(
            CompanyStudentAccess.access_grant_id == grant_id,
            CompanyStudentAccess.student_id == student_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Dodela nije pronađena.")
    g = db.query(AccessGrant).filter(AccessGrant.id == grant_id).first()
    db.delete(row)
    if g and (g.used_cv_count or 0) > 0:
        g.used_cv_count = g.used_cv_count - 1
    db.commit()
    return {"ok": True}


@router.post("/students/{student_id}/edit-grant", response_model=dict)
def grant_edit(
    student_id: int,
    body: EditGrantBody,
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    st = db.query(Student).filter(Student.id == student_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Student nije pronađen.")
    db.add(EditGrant(student_id=st.id, granted_by_user_id=admin.id, reason=body.reason, consumed=False))
    db.commit()
    return {"ok": True}


@router.post("/students/import", response_model=dict)
def import_students_csv(
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    raw = file.file.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(raw))
    required = {"email", "name", "password", "ime", "prezime", "fakultet_id"}
    if reader.fieldnames is None or not required.issubset({h.strip().lower() for h in reader.fieldnames}):
        raise HTTPException(status_code=400, detail=f"CSV mora sadržati kolone: {sorted(required)}")
    created = 0
    fn = {k.strip().lower(): k for k in reader.fieldnames}
    for row in reader:
        def g(key: str) -> str:
            return (row.get(fn[key]) or "").strip()

        email = g("email")
        if not email:
            continue
        if db.query(User).filter(User.email == email).first():
            continue
        try:
            hashed = get_password_hash(g("password"))
        except ValueError:
            continue
        fid = int(g("fakultet_id"))
        if not db.query(Fakultet).filter(Fakultet.id == fid).first():
            continue
        u = User(
            name=g("name") or email,
            email=email,
            role=ROLE_STUDENT,
            hashed_password=hashed,
            is_active=True,
            email_verified=True,
            admin_approved=True,
            consent_data_processing_at=datetime.now(timezone.utc),
        )
        db.add(u)
        db.flush()
        st = Student(
            user_id=u.id,
            ime=g("ime"),
            prezime=g("prezime"),
            fakultet_id=fid,
            last_edit_at=datetime.now(timezone.utc),
        )
        db.add(st)
        created += 1
    db.commit()
    audit_service.write_audit(
        db,
        user_id=admin.id,
        action="admin_bulk_import_students",
        resource_type="import",
        resource_id=None,
        ip_address=client_ip_ctx.get(),
        request_id=request_id_ctx.get(),
        details={"created": created},
    )
    db.commit()
    return {"created": created}


@router.get("/audit-log")
def audit_log(
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    if user_id is not None:
        q = q.filter(AuditLog.user_id == user_id)
    if date_from:
        q = q.filter(AuditLog.created_at >= date_from)
    if date_to:
        q = q.filter(AuditLog.created_at <= date_to)
    total = q.count()
    rows = q.order_by(AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "ip_address": r.ip_address,
                "request_id": r.request_id,
                "details": r.details,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/analytics", response_model=dict)
def analytics(admin: CurrentAdmin, db: Session = Depends(get_db)):
    student_users = db.query(func.count(User.id)).filter(User.role == ROLE_STUDENT).scalar() or 0
    pending = (
        db.query(func.count(User.id))
        .filter(User.role == ROLE_STUDENT, User.admin_approved == False, User.email_verified == True)  # noqa: E712
        .scalar()
        or 0
    )
    companies = db.query(func.count(User.id)).filter(User.role == ROLE_COMPANY).scalar() or 0
    by_faculty = (
        db.query(Fakultet.naziv, func.count(Student.id))
        .join(Student, Student.fakultet_id == Fakultet.id)
        .group_by(Fakultet.naziv)
        .all()
    )
    return {
        "student_users": student_users,
        "pending_student_approvals": pending,
        "company_users": companies,
        "students_by_faculty": [{"faculty": a[0], "count": a[1]} for a in by_faculty],
    }


@router.get("/deletion-requests", response_model=List[dict])
def list_deletion_requests(admin: CurrentAdmin, db: Session = Depends(get_db)):
    rows = db.query(DeletionRequest).filter(DeletionRequest.status == "pending").all()
    out = []
    for r in rows:
        u = db.query(User).filter(User.id == r.user_id).first()
        out.append(
            {
                "id": r.id,
                "user_id": r.user_id,
                "email": u.email if u else None,
                "requested_at": r.requested_at.isoformat() if r.requested_at else None,
            }
        )
    return out


@router.post("/deletion-requests/{request_id}/process")
def process_deletion(
    request_id: int,
    body: DeletionProcessBody,
    admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    req = db.query(DeletionRequest).filter(DeletionRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Zahtev nije pronađen.")
    if not body.approve:
        req.status = "rejected"
        req.processed_at = datetime.now(timezone.utc)
        req.processed_by_user_id = admin.id
        req.note = body.note
        db.commit()
        return {"ok": True}
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik ne postoji.")
    from ..services import file_storage as file_storage_service

    st = db.query(Student).filter(Student.user_id == user.id).first()
    if st and st.cv_file_path:
        file_storage_service.delete_cv_file(st.cv_file_path)
    audit_service.write_audit(
        db,
        user_id=admin.id,
        action="admin_process_deletion",
        resource_type="user",
        resource_id=user.id,
        ip_address=client_ip_ctx.get(),
        request_id=request_id_ctx.get(),
        details={"approve": True},
    )
    db.delete(user)
    db.commit()
    return {"ok": True}
