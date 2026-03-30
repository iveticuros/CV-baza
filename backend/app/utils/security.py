from __future__ import annotations

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from ..config import settings
from ..schemas.user import TokenData

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$"
)


def validate_password_strength(password: str) -> None:
    if not _PASSWORD_PATTERN.match(password):
        raise ValueError(
            "Lozinka mora imati najmanje 12 karaktera, veliko i malo slovo, "
            "cifru i specijalni karakter."
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    validate_password_strength(password)
    return pwd_context.hash(password)


def create_access_token(
    *,
    email: str,
    user_id: int,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode: dict[str, Any] = {
        "sub": email,
        "uid": user_id,
        "role": role,
    }
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        uid = payload.get("uid")
        role = payload.get("role")
        if email is None or uid is None:
            return None
        return TokenData(email=str(email), user_id=int(uid), role=str(role) if role else None)
    except InvalidTokenError:
        return None


def create_email_token(
    *,
    email: str,
    purpose: str,
    expires_hours: int,
) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    payload = {"sub": email, "purpose": purpose, "exp": exp}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_email_token(token: str, purpose: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("purpose") != purpose:
            return None
        email = payload.get("sub")
        return str(email) if email else None
    except InvalidTokenError:
        return None


def generate_refresh_token_value() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
