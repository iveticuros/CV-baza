from __future__ import annotations

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only-32chars")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("PII_ENCRYPTION_KEY", "__QJEPgWMAZWydpUjfWURbAq6r14Rxi7GXyO70tyNCo=")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "10000")
os.environ.setdefault("AUTH_RATE_LIMIT_PER_MINUTE", "10000")
os.environ.setdefault("DOWNLOAD_RATE_LIMIT_PER_MINUTE", "10000")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import (  # noqa: F401
    User, Student, Fakultet, StudijskiProgram, Tehnologija,
    Projekat, CompanyProfile, AccessGrant, CompanyStudentAccess,
    AuditLog, RefreshToken, EditGrant, DeletionRequest,
)
from app.utils.security import get_password_hash

TEST_DB_URL = "sqlite://"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


VALID_PASSWORD = "TestPassword1!"


def make_user(db, *, email="test@test.com", role="student", verified=True, approved=True, active=True):
    u = User(
        name="Test User",
        email=email,
        role=role,
        hashed_password=get_password_hash(VALID_PASSWORD),
        is_active=active,
        email_verified=verified,
        admin_approved=approved,
        failed_login_attempts=0,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def login_user(client, email="test@test.com", password=VALID_PASSWORD):
    resp = client.post("/auth/token", data={"username": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def make_fakultet(db, naziv="FTN"):
    f = Fakultet(naziv=naziv)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def make_student(db, user_id, fakultet_id):
    st = Student(
        user_id=user_id, ime="Test", prezime="Student",
        fakultet_id=fakultet_id,
    )
    db.add(st)
    db.commit()
    db.refresh(st)
    return st
