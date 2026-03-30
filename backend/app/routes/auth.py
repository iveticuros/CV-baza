from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import insert
from sqlalchemy.orm import Session

from ..config import settings
from ..rate_limit import limiter
from ..constants import REFRESH_COOKIE_NAME, ROLE_STUDENT
from ..database import get_db
from ..models.projekat import Projekat
from ..models.refresh_token import RefreshToken
from ..models.student import Student
from ..models.fakultet import Fakultet
from ..models.tehnologija import Tehnologija, student_tehnologija
from ..models.user import User
from ..schemas.register import StudentRegisterRequest
from ..schemas.user import LoginResponse, MessageResponse, PasswordResetConfirm, PasswordResetRequest, Token, UserPublic
from ..services import audit as audit_service
from ..services import email as email_service
from ..request_context import client_ip_ctx, request_id_ctx
from ..utils.auth import get_current_active_user
from ..utils.security import (
    create_access_token,
    create_email_token,
    generate_refresh_token_value,
    get_password_hash,
    hash_refresh_token,
    verify_email_token,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _user_public(u: User) -> UserPublic:
    return UserPublic.model_validate(u)


def _set_refresh_cookie(response: Response, raw: str) -> None:
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=max_age,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/")


def _persist_refresh_token(db: Session, user_id: int, raw: str) -> None:
    token_hash = hash_refresh_token(raw)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    row = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at, revoked=False)
    db.add(row)
    db.commit()


def _revoke_all_refresh(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).update({"revoked": True})
    db.commit()


def _issue_login(db: Session, user: User, response: Response) -> LoginResponse:
    access = create_access_token(
        email=user.email,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    raw_refresh = generate_refresh_token_value()
    _persist_refresh_token(db, user.id, raw_refresh)
    _set_refresh_cookie(response, raw_refresh)
    return LoginResponse(access_token=access, token_type="bearer", user=_user_public(user))


def _check_login_allowed(user: User) -> None:
    now = datetime.now(timezone.utc)
    locked = user.locked_until
    if locked and not locked.tzinfo:
        locked = locked.replace(tzinfo=timezone.utc)
    if locked and locked > now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nalog je privremeno zaključan zbog neuspešnih prijava.",
        )
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Potvrdite email adresu pre prijave.",
        )
    if not user.admin_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nalog čeka odobrenje administratora.",
        )


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
async def register_student(
    request: Request,
    body: StudentRegisterRequest,
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email je već registrovan.")
    if not db.query(Fakultet).filter(Fakultet.id == body.fakultet_id).first():
        raise HTTPException(status_code=400, detail="Neispravan fakultet.")
    try:
        hashed = get_password_hash(body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    user = User(
        name=body.name,
        email=body.email,
        role=ROLE_STUDENT,
        hashed_password=hashed,
        is_active=True,
        email_verified=False,
        admin_approved=False,
        consent_data_processing_at=datetime.now(timezone.utc),
        failed_login_attempts=0,
    )
    db.add(user)
    db.flush()

    dr = body.datum_rodjenja.isoformat() if body.datum_rodjenja else None
    st = Student(
        user_id=user.id,
        ime=body.ime,
        prezime=body.prezime,
        kontakt_telefon=body.kontakt_telefon,
        datum_rodjenja_enc=dr,
        adresa=body.adresa,
        prosek=body.prosek,
        fakultet_id=body.fakultet_id,
        last_edit_at=datetime.now(timezone.utc),
    )
    db.add(st)
    db.flush()
    for p in body.projekti:
        db.add(
            Projekat(
                datum_pocetka_izrade=p.datum_pocetka_izrade,
                datum_kraja_izrade_projekta=p.datum_kraja_izrade_projekta,
                opis=p.opis,
                id_studenta=st.id,
            )
        )
    if body.tehnologija_ids:
        for tid in body.tehnologija_ids:
            if db.query(Tehnologija).filter(Tehnologija.id == tid).first():
                db.execute(insert(student_tehnologija).values(student_id=st.id, tehnologija_id=tid))

    token = create_email_token(
        email=user.email,
        purpose="email_verify",
        expires_hours=settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS,
    )
    audit_service.write_audit(
        db,
        user_id=user.id,
        action="register_student",
        resource_type="user",
        resource_id=user.id,
        ip_address=client_ip_ctx.get(),
        request_id=request_id_ctx.get(),
    )
    db.commit()
    try:
        await email_service.send_verification_email(user.email, token)
    except Exception:
        pass
    return MessageResponse(
        message="Registracija primljena. Proverite email za potvrdu naloga; administrator mora odobriti pristup."
    )


@router.get("/verify-email", response_model=MessageResponse)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    email = verify_email_token(token, "email_verify")
    if not email:
        raise HTTPException(status_code=400, detail="Nevažeći ili istekao link.")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    user.email_verified = True
    db.commit()
    return MessageResponse(message="Email potvrđen.")


@router.post("/token", response_model=LoginResponse)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    now = datetime.now(timezone.utc)
    if not user or not verify_password(form_data.password, user.hashed_password):
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=settings.LOCKOUT_MINUTES)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Neispravan email ili lozinka.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Nalog je deaktiviran.")
    _check_login_allowed(user)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    return _issue_login(db, user, response)


@router.post("/refresh", response_model=Token)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    raw = request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw:
        raise HTTPException(status_code=401, detail="Nema refresh sesije.")
    th = hash_refresh_token(raw)
    row = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == th, RefreshToken.revoked == False)  # noqa: E712
        .first()
    )
    exp = row.expires_at if row else None
    if exp and not exp.tzinfo:
        exp = exp.replace(tzinfo=timezone.utc)
    if not row or (exp and exp < datetime.now(timezone.utc)):
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Istekla sesija.")
    user = db.query(User).filter(User.id == row.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Nevažeća sesija.")
    _check_login_allowed(user)
    row.revoked = True
    db.commit()
    access = create_access_token(
        email=user.email,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_raw = generate_refresh_token_value()
    _persist_refresh_token(db, user.id, new_raw)
    _set_refresh_cookie(response, new_raw)
    return Token(access_token=access, token_type="bearer")


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _revoke_all_refresh(db, current_user.id)
    _clear_refresh_cookie(response)
    return MessageResponse(message="Odjavljeni ste.")


@router.post("/password-reset/request", response_model=MessageResponse)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
async def request_password_reset(
    request: Request,
    body: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == body.email).first()
    if user and user.is_active:
        token = create_email_token(
            email=user.email,
            purpose="password_reset",
            expires_hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
        )
        try:
            await email_service.send_password_reset_email(user.email, token)
        except Exception:
            pass
    return MessageResponse(message="Ako nalog postoji, link za resetovanje lozinke je poslat na email.")


@router.post("/password-reset/confirm", response_model=MessageResponse)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
def confirm_password_reset(
    request: Request,
    body: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    email = verify_email_token(body.token, "password_reset")
    if not email:
        raise HTTPException(status_code=400, detail="Nevažeći ili istekao link za resetovanje.")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    try:
        hashed = get_password_hash(body.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    user.hashed_password = hashed
    _revoke_all_refresh(db, user.id)
    db.commit()
    return MessageResponse(message="Lozinka je uspešno promenjena.")


@router.get("/verify-token")
def verify_user_token(current_user: User = Depends(get_current_active_user)):
    return {"valid": True, "user": _user_public(current_user).model_dump()}


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_active_user)):
    return _user_public(current_user)


@router.get("/profile", response_model=UserPublic)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return _user_public(current_user)
