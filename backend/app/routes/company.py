from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..config import settings
from ..rate_limit import limiter
from ..database import get_db
from ..models.access_grant import AccessGrant
from ..models.company_profile import CompanyProfile
from ..models.company_student_access import CompanyStudentAccess
from ..models.fakultet import Fakultet
from ..models.student import Student
from ..models.tehnologija import Tehnologija, student_tehnologija
from ..models.user import User
from ..schemas.student import PaginatedStudents, StudentPublicCompany
from ..services import audit as audit_service
from ..services import file_storage as file_storage_service
from ..request_context import client_ip_ctx, request_id_ctx
from ..utils.auth import CurrentCompany


class CompanyProfileOut(BaseModel):
    id: int
    company_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CompanyProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=300)
    contact_person: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class AccessGrantOut(BaseModel):
    id: int
    max_cv_count: int
    used_cv_count: int
    valid_from: date
    valid_until: date
    active: bool


router = APIRouter(prefix="/company", tags=["Company"])


def _company_profile(db: Session, user: User) -> CompanyProfile:
    p = db.query(CompanyProfile).filter(CompanyProfile.user_id == user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profil kompanije ne postoji.")
    return p


def _active_grants_query(db: Session, company_profile_id: int):
    today = date.today()
    return (
        db.query(AccessGrant)
        .filter(
            AccessGrant.company_profile_id == company_profile_id,
            AccessGrant.revoked_at.is_(None),
            AccessGrant.valid_from <= today,
            AccessGrant.valid_until >= today,
        )
    )


def _student_ids_accessible(db: Session, company_profile_id: int) -> List[int]:
    grant_ids = [g.id for g in _active_grants_query(db, company_profile_id).all()]
    if not grant_ids:
        return []
    rows = (
        db.query(CompanyStudentAccess.student_id)
        .filter(CompanyStudentAccess.access_grant_id.in_(grant_ids))
        .distinct()
        .all()
    )
    return [r[0] for r in rows]


def _ensure_company_can_view_student(db: Session, company_profile_id: int, student_id: int) -> None:
    grant_ids = [g.id for g in _active_grants_query(db, company_profile_id).all()]
    ok = (
        db.query(CompanyStudentAccess)
        .filter(
            CompanyStudentAccess.access_grant_id.in_(grant_ids),
            CompanyStudentAccess.student_id == student_id,
        )
        .first()
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Student nije dostupan.")


def _build_student_public(db: Session, st: Student) -> StudentPublicCompany:
    fac = db.query(Fakultet).filter(Fakultet.id == st.fakultet_id).first()
    fac_name = fac.naziv if fac else None
    tech = (
        db.query(Tehnologija.naziv)
        .join(student_tehnologija, student_tehnologija.c.tehnologija_id == Tehnologija.id)
        .filter(student_tehnologija.c.student_id == st.id)
        .all()
    )
    names = [t[0] for t in tech]
    return StudentPublicCompany(
        id=st.id,
        ime=st.ime,
        prezime=st.prezime,
        prosek=st.prosek,
        fakultet_id=st.fakultet_id,
        faculty_name=fac_name,
        tehnologije=names,
    )


@router.get("/profile", response_model=CompanyProfileOut)
def get_company_profile(user: CurrentCompany, db: Session = Depends(get_db)):
    p = _company_profile(db, user)
    return p


@router.put("/profile", response_model=CompanyProfileOut)
def update_company_profile(
    body: CompanyProfileUpdate,
    user: CurrentCompany,
    db: Session = Depends(get_db),
):
    p = _company_profile(db, user)
    if body.company_name is not None:
        p.company_name = body.company_name
    if body.contact_person is not None:
        p.contact_person = body.contact_person
    if body.phone is not None:
        p.phone = body.phone
    if body.description is not None:
        p.description = body.description
    db.commit()
    return p


@router.get("/access", response_model=List[AccessGrantOut])
def list_access(user: CurrentCompany, db: Session = Depends(get_db)):
    p = _company_profile(db, user)
    today = date.today()
    rows = db.query(AccessGrant).filter(AccessGrant.company_profile_id == p.id, AccessGrant.revoked_at.is_(None)).all()
    out = []
    for g in rows:
        active = g.valid_from <= today <= g.valid_until
        out.append(
            AccessGrantOut(
                id=g.id,
                max_cv_count=g.max_cv_count,
                used_cv_count=g.used_cv_count,
                valid_from=g.valid_from,
                valid_until=g.valid_until,
                active=active,
            )
        )
    return out


@router.get("/students", response_model=PaginatedStudents)
def list_students(
    user: CurrentCompany,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
    fakultet_id: Optional[int] = None,
    min_prosek: Optional[float] = None,
    max_prosek: Optional[float] = None,
    tehnologija_id: Optional[int] = None,
):
    p = _company_profile(db, user)
    ids = _student_ids_accessible(db, p.id)
    if not ids:
        return PaginatedStudents(items=[], total=0, page=page, page_size=page_size)
    query = db.query(Student).filter(Student.id.in_(ids))
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Student.ime.ilike(like), Student.prezime.ilike(like)))
    if fakultet_id is not None:
        query = query.filter(Student.fakultet_id == fakultet_id)
    if min_prosek is not None:
        query = query.filter(Student.prosek >= min_prosek)
    if max_prosek is not None:
        query = query.filter(Student.prosek <= max_prosek)
    if tehnologija_id is not None:
        query = query.join(
            student_tehnologija,
            student_tehnologija.c.student_id == Student.id,
        ).filter(student_tehnologija.c.tehnologija_id == tehnologija_id)
    total = query.distinct().count()
    rows = (
        query.distinct()
        .order_by(Student.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [_build_student_public(db, st) for st in rows]
    return PaginatedStudents(items=items, total=total, page=page, page_size=page_size)


@router.get("/students/{student_id}", response_model=StudentPublicCompany)
def get_student_detail(
    student_id: int,
    user: CurrentCompany,
    db: Session = Depends(get_db),
):
    p = _company_profile(db, user)
    _ensure_company_can_view_student(db, p.id, student_id)
    st = db.query(Student).filter(Student.id == student_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Student nije pronađen.")
    return _build_student_public(db, st)


@router.get("/students/{student_id}/cv")
@limiter.limit(f"{settings.DOWNLOAD_RATE_LIMIT_PER_MINUTE}/minute")
def download_student_cv(
    request: Request,
    student_id: int,
    user: CurrentCompany,
    db: Session = Depends(get_db),
):
    p = _company_profile(db, user)
    _ensure_company_can_view_student(db, p.id, student_id)
    st = db.query(Student).filter(Student.id == student_id).first()
    if not st or not st.cv_file_path:
        raise HTTPException(status_code=404, detail="CV nije dostupan.")
    try:
        data = file_storage_service.read_cv_file(st.cv_file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fajl nije pronađen.") from None
    audit_service.write_audit(
        db,
        user_id=user.id,
        action="company_download_cv",
        resource_type="student",
        resource_id=student_id,
        ip_address=client_ip_ctx.get(),
        request_id=request_id_ctx.get(),
    )
    db.commit()
    return Response(
        content=data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{st.cv_original_filename or "cv.pdf"}"'
        },
    )
