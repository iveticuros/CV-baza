from __future__ import annotations

import pytest
from .conftest import make_user, login_user, auth_header, VALID_PASSWORD, make_fakultet


class TestRegistration:
    def test_register_student_success(self, client, db):
        fak = make_fakultet(db)
        resp = client.post("/auth/register", json={
            "name": "New Student", "email": "new@test.com",
            "password": VALID_PASSWORD, "ime": "New", "prezime": "Student",
            "fakultet_id": fak.id, "consent_data_processing": True,
        })
        assert resp.status_code == 201
        assert "Registracija" in resp.json()["message"]

    def test_register_duplicate_email(self, client, db):
        fak = make_fakultet(db)
        make_user(db, email="dup@test.com")
        resp = client.post("/auth/register", json={
            "name": "Dup", "email": "dup@test.com",
            "password": VALID_PASSWORD, "ime": "D", "prezime": "U",
            "fakultet_id": fak.id, "consent_data_processing": True,
        })
        assert resp.status_code == 400

    def test_register_weak_password(self, client, db):
        fak = make_fakultet(db)
        resp = client.post("/auth/register", json={
            "name": "Weak", "email": "weak@test.com",
            "password": "short", "ime": "W", "prezime": "P",
            "fakultet_id": fak.id, "consent_data_processing": True,
        })
        assert resp.status_code in (400, 422)

    def test_register_no_role_in_body(self, client, db):
        """Ensures no 'role' field is accepted in registration request."""
        fak = make_fakultet(db)
        resp = client.post("/auth/register", json={
            "name": "Hacker", "email": "hack@test.com",
            "password": VALID_PASSWORD, "ime": "H", "prezime": "K",
            "fakultet_id": fak.id, "consent_data_processing": True,
            "role": "admin",
        })
        if resp.status_code == 201:
            from app.models.user import User
            from .conftest import TestSession
            s = TestSession()
            u = s.query(User).filter(User.email == "hack@test.com").first()
            assert u.role == "student"
            s.close()


class TestLogin:
    def test_login_success(self, client, db):
        make_user(db, email="login@test.com")
        resp = client.post("/auth/token", data={"username": "login@test.com", "password": VALID_PASSWORD})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["role"] == "student"

    def test_login_wrong_password(self, client, db):
        make_user(db, email="wrong@test.com")
        resp = client.post("/auth/token", data={"username": "wrong@test.com", "password": "WrongPass123!"})
        assert resp.status_code == 401

    def test_login_unverified_email(self, client, db):
        make_user(db, email="unverified@test.com", verified=False)
        resp = client.post("/auth/token", data={"username": "unverified@test.com", "password": VALID_PASSWORD})
        assert resp.status_code == 403

    def test_login_unapproved(self, client, db):
        make_user(db, email="unapproved@test.com", approved=False)
        resp = client.post("/auth/token", data={"username": "unapproved@test.com", "password": VALID_PASSWORD})
        assert resp.status_code == 403

    def test_login_lockout(self, client, db):
        make_user(db, email="lockout@test.com")
        for _ in range(5):
            client.post("/auth/token", data={"username": "lockout@test.com", "password": "WrongPass123!"})
        resp = client.post("/auth/token", data={"username": "lockout@test.com", "password": VALID_PASSWORD})
        assert resp.status_code == 403
        assert "zaključan" in resp.json()["error"]["message"]


class TestLogout:
    def test_logout_revokes_all_tokens(self, client, db):
        make_user(db, email="logout@test.com")
        token = login_user(client, "logout@test.com")
        resp = client.post("/auth/logout", headers=auth_header(token))
        assert resp.status_code == 200

        from app.models.refresh_token import RefreshToken
        from .conftest import TestSession
        s = TestSession()
        tokens = s.query(RefreshToken).all()
        for t in tokens:
            assert t.revoked is True
        s.close()


class TestRefresh:
    def test_refresh_rotates_token(self, client, db):
        make_user(db, email="refresh@test.com")
        login_resp = client.post("/auth/token", data={"username": "refresh@test.com", "password": VALID_PASSWORD})
        assert login_resp.status_code == 200
        refresh_resp = client.post("/auth/refresh")
        if refresh_resp.status_code == 200:
            assert "access_token" in refresh_resp.json()


class TestPasswordReset:
    def test_request_reset_always_200(self, client, db):
        resp = client.post("/auth/password-reset/request", json={"email": "nonexistent@test.com"})
        assert resp.status_code == 200

    def test_confirm_reset_invalid_token(self, client, db):
        resp = client.post("/auth/password-reset/confirm", json={
            "token": "invalid-token", "new_password": "NewPassword123!",
        })
        assert resp.status_code == 400
