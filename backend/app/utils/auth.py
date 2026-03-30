from typing import Annotated, Callable, Optional, TypeVar

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..constants import ALL_ROLES
from ..database import get_db
from ..models.user import User
from .security import verify_access_token

security_scheme = HTTPBearer(auto_error=False)

T = TypeVar("T")


def get_token_from_credentials(
    creds: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security_scheme)],
) -> str:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niste prijavljeni.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return creds.credentials


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(get_token_from_credentials),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nevažeći pristupni token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token)
    if token_data is None or token_data.email is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    if token_data.user_id is not None and user.id != token_data.user_id:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Nalog je deaktiviran.")
    if not current_user.email_verified:
        raise HTTPException(status_code=403, detail="Potvrdite email adresu.")
    if not current_user.admin_approved:
        raise HTTPException(status_code=403, detail="Nalog čeka odobrenje administratora.")
    return current_user


def require_role(*allowed_roles: str) -> Callable[..., User]:
    allowed = set(allowed_roles)
    for r in allowed:
        if r not in ALL_ROLES:
            raise ValueError(f"Unknown role: {r}")

    def _dep(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nemate dozvolu za ovu radnju.",
            )
        return current_user

    return _dep


CurrentAdmin = Annotated[User, Depends(require_role("admin"))]
CurrentStudent = Annotated[User, Depends(require_role("student"))]
CurrentCompany = Annotated[User, Depends(require_role("company"))]
