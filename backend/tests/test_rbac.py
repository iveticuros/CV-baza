from __future__ import annotations

from .conftest import make_user, login_user, auth_header, make_fakultet, make_student


class TestRoleEscalation:
    """Ensure users cannot access routes outside their role."""

    def test_student_cannot_access_admin(self, client, db):
        make_user(db, email="s@test.com", role="student")
        tok = login_user(client, "s@test.com")
        resp = client.get("/admin/users", headers=auth_header(tok))
        assert resp.status_code == 403

    def test_student_cannot_access_company(self, client, db):
        make_user(db, email="s2@test.com", role="student")
        tok = login_user(client, "s2@test.com")
        resp = client.get("/company/profile", headers=auth_header(tok))
        assert resp.status_code in (403, 404)

    def test_company_cannot_access_admin(self, client, db):
        make_user(db, email="c@test.com", role="company")
        tok = login_user(client, "c@test.com")
        resp = client.get("/admin/users", headers=auth_header(tok))
        assert resp.status_code == 403

    def test_company_cannot_access_student_profile(self, client, db):
        make_user(db, email="c2@test.com", role="company")
        tok = login_user(client, "c2@test.com")
        resp = client.get("/students/profile", headers=auth_header(tok))
        assert resp.status_code in (403, 404)

    def test_unauthenticated_cannot_access_admin(self, client, db):
        resp = client.get("/admin/users")
        assert resp.status_code in (401, 403)

    def test_unauthenticated_cannot_access_student(self, client, db):
        resp = client.get("/students/profile")
        assert resp.status_code in (401, 403)


class TestStudentRouteAccess:
    def test_student_can_view_own_profile(self, client, db):
        fak = make_fakultet(db)
        u = make_user(db, email="student@test.com", role="student")
        make_student(db, u.id, fak.id)
        tok = login_user(client, "student@test.com")
        resp = client.get("/students/profile", headers=auth_header(tok))
        assert resp.status_code == 200
        assert resp.json()["ime"] == "Test"


class TestAdminRouteAccess:
    def test_admin_can_list_users(self, client, db):
        make_user(db, email="admin@test.com", role="admin")
        tok = login_user(client, "admin@test.com")
        resp = client.get("/admin/users", headers=auth_header(tok))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_admin_can_view_analytics(self, client, db):
        make_user(db, email="admin2@test.com", role="admin")
        tok = login_user(client, "admin2@test.com")
        resp = client.get("/admin/analytics", headers=auth_header(tok))
        assert resp.status_code == 200
        data = resp.json()
        assert "student_users" in data

    def test_admin_can_view_audit_log(self, client, db):
        make_user(db, email="admin3@test.com", role="admin")
        tok = login_user(client, "admin3@test.com")
        resp = client.get("/admin/audit-log", headers=auth_header(tok))
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
