from __future__ import annotations

from .conftest import make_user, login_user, auth_header, VALID_PASSWORD, make_fakultet, make_student


class TestAdminUserManagement:
    def test_create_company_user(self, client, db):
        make_user(db, email="admin@test.com", role="admin")
        tok = login_user(client, "admin@test.com")
        resp = client.post("/admin/users", headers=auth_header(tok), json={
            "name": "Test Co", "email": "company@test.com",
            "password": VALID_PASSWORD, "role": "company",
        })
        assert resp.status_code == 201
        assert resp.json()["role"] == "company"

    def test_cannot_create_student_via_admin(self, client, db):
        make_user(db, email="admin2@test.com", role="admin")
        tok = login_user(client, "admin2@test.com")
        resp = client.post("/admin/users", headers=auth_header(tok), json={
            "name": "S", "email": "s@test.com",
            "password": VALID_PASSWORD, "role": "student",
        })
        assert resp.status_code == 400

    def test_deactivate_user(self, client, db):
        make_user(db, email="admin3@test.com", role="admin")
        target = make_user(db, email="target@test.com", role="student")
        tok = login_user(client, "admin3@test.com")
        resp = client.put(f"/admin/users/{target.id}", headers=auth_header(tok), json={"is_active": False})
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_reset_password(self, client, db):
        make_user(db, email="admin4@test.com", role="admin")
        target = make_user(db, email="target2@test.com", role="student")
        tok = login_user(client, "admin4@test.com")
        resp = client.put(f"/admin/users/{target.id}", headers=auth_header(tok), json={
            "password": "NewPassword456!",
        })
        assert resp.status_code == 200

    def test_approve_student(self, client, db):
        make_user(db, email="admin5@test.com", role="admin")
        s = make_user(db, email="pending@test.com", role="student", approved=False)
        tok = login_user(client, "admin5@test.com")
        resp = client.post(f"/admin/users/{s.id}/approve-student", headers=auth_header(tok))
        assert resp.status_code == 200
        assert resp.json()["admin_approved"] is True

    def test_delete_user(self, client, db):
        make_user(db, email="admin6@test.com", role="admin")
        target = make_user(db, email="del@test.com", role="student")
        tok = login_user(client, "admin6@test.com")
        resp = client.delete(f"/admin/users/{target.id}", headers=auth_header(tok))
        assert resp.status_code == 204

    def test_cannot_delete_self(self, client, db):
        admin = make_user(db, email="admin7@test.com", role="admin")
        tok = login_user(client, "admin7@test.com")
        resp = client.delete(f"/admin/users/{admin.id}", headers=auth_header(tok))
        assert resp.status_code == 400


class TestAccessGrants:
    def _setup(self, db):
        from app.models.company_profile import CompanyProfile
        admin = make_user(db, email="adm@test.com", role="admin")
        co = make_user(db, email="co@test.com", role="company")
        db.add(CompanyProfile(user_id=co.id, company_name="TestCo", contact_person="X"))
        db.commit()
        return admin, co

    def test_create_grant(self, client, db):
        admin, co = self._setup(db)
        tok = login_user(client, "adm@test.com")
        resp = client.post("/admin/access-grants", headers=auth_header(tok), json={
            "company_user_id": co.id, "max_cv_count": 10,
            "valid_from": "2025-01-01", "valid_until": "2025-12-31",
        })
        assert resp.status_code == 200
        assert "id" in resp.json()

    def test_update_grant(self, client, db):
        admin, co = self._setup(db)
        tok = login_user(client, "adm@test.com")
        create_resp = client.post("/admin/access-grants", headers=auth_header(tok), json={
            "company_user_id": co.id, "max_cv_count": 10,
            "valid_from": "2025-01-01", "valid_until": "2025-12-31",
        })
        gid = create_resp.json()["id"]
        resp = client.put(f"/admin/access-grants/{gid}", headers=auth_header(tok), json={
            "max_cv_count": 20,
        })
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_revoke_grant(self, client, db):
        admin, co = self._setup(db)
        tok = login_user(client, "adm@test.com")
        create_resp = client.post("/admin/access-grants", headers=auth_header(tok), json={
            "company_user_id": co.id, "max_cv_count": 5,
            "valid_from": "2025-01-01", "valid_until": "2025-12-31",
        })
        gid = create_resp.json()["id"]
        resp = client.post(f"/admin/access-grants/{gid}/revoke", headers=auth_header(tok))
        assert resp.status_code == 200


class TestEditGrant:
    def test_grant_edit(self, client, db):
        fak = make_fakultet(db)
        admin = make_user(db, email="adm2@test.com", role="admin")
        s = make_user(db, email="st@test.com", role="student")
        st = make_student(db, s.id, fak.id)
        tok = login_user(client, "adm2@test.com")
        resp = client.post(f"/admin/students/{st.id}/edit-grant", headers=auth_header(tok), json={
            "reason": "test grant",
        })
        assert resp.status_code == 200
