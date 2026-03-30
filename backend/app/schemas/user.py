from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRole(str, Enum):
    student = "student"
    admin = "admin"
    company = "company"


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    email_verified: bool = False
    admin_approved: bool = False

    class Config:
        from_attributes = True


class UserCreateAdmin(BaseModel):
    """Admin-created users (company or admin). Student self-registration uses StudentRegisterRequest."""

    name: str = Field(..., max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    role: UserRole


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=12, max_length=128)
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None
    admin_approved: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(Token):
    user: UserPublic


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class MessageResponse(BaseModel):
    message: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=12, max_length=128)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12, max_length=128)
