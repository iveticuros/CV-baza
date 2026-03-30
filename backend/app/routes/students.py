import json
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from ..config import settings
from ..rate_limit import limiter
from ..database import get_db
from ..models.deletion_request import DeletionRequest
from ..models.edit_grant import EditGrant
from ..models.fakultet import Fakultet
from ..models.projekat import Projekat
from ..models.student import Student
from ..models.tehnologija import Tehnologija, student_tehnologija
from ..models.user import User
from ..schemas.student import ProjekatOut, StudentProfileOut, StudentProfileUpdate, TehnologijaOut
from ..schemas.user import MessageResponse
from ..services import audit as audit_service
from ..services import file_storage as file_storage_service
from ..request_context import client_ip_ctx, request_id_ctx
from ..utils.auth import CurrentStudent

router = APIRouter(prefix="/students", tags=["Students"])

EDIT_COOLDOWN_DAYS = 30


def _parse_birth(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def _build_profile_out(db: Session, st: Student) -> StudentProfileOut:
    fac = db.query(Fakultet).filter(Fakultet.id == st.fakultet_id).first()
    fac_name = fac.naziv if fac else None
    proj = db.query(Projekat).filter(Projekat.id_studenta == st.id).all()
    t_rows = (
        db.query(Tehnologija)
        .join(student_tehnologija, student_tehnologija.c.tehnologija_id == Tehnologija.id)
        .filter(student_tehnologija.c.student_id == st.id)
        .all()
    )
    can_edit = True
    reason_until = None
    grant = (
        db.query(EditGrant)
        .filter(EditGrant.student_id == st.id, EditGrant.consumed == False)  # noqa: E712
        .first()
    )
    if st.last_edit_at and not grant:
        last_edit = st.last_edit_at if st.last_edit_at.tzinfo else st.last_edit_at.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - last_edit
        if delta < timedelta(days=EDIT_COOLDOWN_DAYS):
            can_edit = False
            reason_until = st.last_edit_at + timedelta(days=EDIT_COOLDOWN_DAYS)
    return StudentProfileOut(
        id=st.id,
        ime=st.ime,
        prezime=st.prezime,
        kontakt_telefon=st.kontakt_telefon,
        datum_rodjenja=_parse_birth(st.datum_rodjenja_enc),
        adresa=st.adresa,
        prosek=st.prosek,
        fakultet_id=st.fakultet_id,
        faculty_name=fac_name,
        has_cv=bool(st.cv_file_path),
        last_edit_at=st.last_edit_at,
        can_edit_until=None if can_edit else reason_until,
        projekti=[ProjekatOut.model_validate(p) for p in proj],
        tehnologije=[TehnologijaOut.model_validate(t) for t in t_rows],
    )


def _get_student(db: Session, user: User) -> Student:
    st = db.query(Student).filter(Student.user_id == user.id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Profil studenta nije pronađen.")
    return st


@router.get("/profile", response_model=StudentProfileOut)
def get_my_profile(user: CurrentStudent, db: Session = Depends(get_db)):
    st = _get_student(db, user)
    return _build_profile_out(db, st)


@router.put("/profile", response_model=StudentProfileOut)
def update_my_profile(
    user: CurrentStudent,
    body: StudentProfileUpdate,
    db: Session = Depends(get_db),
):
    st = _get_student(db, user)
    grant = (
        db.query(EditGrant)
        .filter(EditGrant.student_id == st.id, EditGrant.consumed == False)  # noqa: E712
        .order_by(EditGrant.id)
        .first()
    )
    if st.last_edit_at:
        last_edit = st.last_edit_at if st.last_edit_at.tzinfo else st.last_edit_at.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - last_edit
        if delta < timedelta(days=EDIT_COOLDOWN_DAYS) and not grant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Izmena profila dozvoljena je jednom mesečno. Kontaktirajte administratora za dodatnu izmenu.",
            )

    if body.ime is not None:
        st.ime = body.ime
    if body.prezime is not None:
        st.prezime = body.prezime
    if body.kontakt_telefon is not None:
        st.kontakt_telefon = body.kontakt_telefon
    if body.datum_rodjenja is not None:
        st.datum_rodjenja_enc = body.datum_rodjenja.isoformat()
    if body.adresa is not None:
        st.adresa = body.adresa
    if body.prosek is not None:
        st.prosek = body.prosek
    if body.fakultet_id is not None:
        st.fakultet_id = body.fakultet_id

    if body.projekti is not None:
        db.query(Projekat).filter(Projekat.id_studenta == st.id).delete()
        for p in body.projekti:
            db.add(
                Projekat(
                    datum_pocetka_izrade=p.datum_pocetka_izrade,
                    datum_kraja_izrade_projekta=p.datum_kraja_izrade_projekta,
                    opis=p.opis,
                    id_studenta=st.id,
                )
            )
    if body.tehnologija_ids is not None:
        db.execute(delete(student_tehnologija).where(student_tehnologija.c.student_id == st.id))
        for tid in body.tehnologija_ids:
            if db.query(Tehnologija).filter(Tehnologija.id == tid).first():
                db.execute(insert(student_tehnologija).values(student_id=st.id, tehnologija_id=tid))

    st.last_edit_at = datetime.now(timezone.utc)
    if grant:
        grant.consumed = True
    db.commit()
    audit_service.write_audit(
        db,
        user_id=user.id,
        action="student_profile_update",
        resource_type="student",
        resource_id=st.id,
        ip_address=client_ip_ctx.get(),
        request_id=request_id_ctx.get(),
    )
    db.commit()
    return _build_profile_out(db, st)


@router.post("/profile/cv")
async def upload_cv(
    user: CurrentStudent,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    st = _get_student(db, user)
    content = await file.read()
    try:
        rel, orig = file_storage_service.save_cv_file(
            user_id=user.id, content=content, original_filename=file.filename or "cv.pdf",
            content_type=file.content_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if st.cv_file_path:
        file_storage_service.delete_cv_file(st.cv_file_path)
    st.cv_file_path = rel
    st.cv_original_filename = orig
    db.commit()
    audit_service.write_audit(
        db,
        user_id=user.id,
        action="student_cv_upload",
        resource_type="student",
        resource_id=st.id,
        ip_address=client_ip_ctx.get(),
        request_id=request_id_ctx.get(),
    )
    db.commit()
    return MessageResponse(message="CV otpremljen.")


@router.get("/profile/cv")
@limiter.limit(f"{settings.DOWNLOAD_RATE_LIMIT_PER_MINUTE}/minute")
def download_my_cv(request: Request, user: CurrentStudent, db: Session = Depends(get_db)):
    st = _get_student(db, user)
    if not st.cv_file_path:
        raise HTTPException(status_code=404, detail="CV nije otpremljen.")
    try:
        data = file_storage_service.read_cv_file(st.cv_file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fajl nije pronađen.") from None
    return Response(
        content=data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{st.cv_original_filename or "cv.pdf"}"'
        },
    )


@router.delete("/profile/cv", response_model=MessageResponse)
def delete_my_cv(user: CurrentStudent, db: Session = Depends(get_db)):
    st = _get_student(db, user)
    file_storage_service.delete_cv_file(st.cv_file_path)
    st.cv_file_path = None
    st.cv_original_filename = None
    db.commit()
    return MessageResponse(message="CV obrisan.")


@router.get("/profile/export")
def export_my_data(user: CurrentStudent, db: Session = Depends(get_db)):
    st = _get_student(db, user)
    profile = _build_profile_out(db, st)
    payload = {
        "profile": json.loads(profile.model_dump_json()),
        "email": user.email,
        "name": user.name,
    }
    return Response(
        content=json.dumps(payload, default=str, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="my-data-export.json"'},
    )


@router.post("/me/deletion-request", response_model=MessageResponse)
def request_deletion(user: CurrentStudent, db: Session = Depends(get_db)):
    existing = db.query(DeletionRequest).filter(DeletionRequest.user_id == user.id).first()
    if existing and existing.status == "pending":
        return MessageResponse(message="Zahtev je već poslat.")
    if existing:
        existing.status = "pending"
        existing.requested_at = datetime.now(timezone.utc)
    else:
        db.add(DeletionRequest(user_id=user.id, status="pending"))
    db.commit()
    return MessageResponse(message="Zahtev za brisanje je poslat administratoru.")
