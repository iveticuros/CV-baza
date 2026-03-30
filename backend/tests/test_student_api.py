from __future__ import annotations

from .conftest import make_user, login_user, auth_header, make_fakultet, make_student


class TestStudentProfile:
    def test_get_profile(self, client, db):
        fak = make_fakultet(db)
        u = make_user(db, email="profile@test.com")
        make_student(db, u.id, fak.id)
        tok = login_user(client, "profile@test.com")
        resp = client.get("/students/profile", headers=auth_header(tok))
        assert resp.status_code == 200
        assert resp.json()["ime"] == "Test"
        assert resp.json()["faculty_name"] == "FTN"

    def test_update_profile(self, client, db):
        fak = make_fakultet(db)
        u = make_user(db, email="update@test.com")
        make_student(db, u.id, fak.id)
        tok = login_user(client, "update@test.com")
        resp = client.put("/students/profile", headers=auth_header(tok), json={
            "ime": "Updated", "prezime": "Name",
        })
        assert resp.status_code == 200
        assert resp.json()["ime"] == "Updated"

    def test_update_cooldown(self, client, db):
        from datetime import datetime, timezone
        fak = make_fakultet(db)
        u = make_user(db, email="cooldown@test.com")
        st = make_student(db, u.id, fak.id)
        st.last_edit_at = datetime.now(timezone.utc)
        db.commit()
        tok = login_user(client, "cooldown@test.com")
        resp = client.put("/students/profile", headers=auth_header(tok), json={"ime": "Blocked"})
        assert resp.status_code == 403

    def test_export_data(self, client, db):
        fak = make_fakultet(db)
        u = make_user(db, email="export@test.com")
        make_student(db, u.id, fak.id)
        tok = login_user(client, "export@test.com")
        resp = client.get("/students/profile/export", headers=auth_header(tok))
        assert resp.status_code == 200
        assert "profile" in resp.json()

    def test_deletion_request(self, client, db):
        fak = make_fakultet(db)
        u = make_user(db, email="delete@test.com")
        make_student(db, u.id, fak.id)
        tok = login_user(client, "delete@test.com")
        resp = client.post("/students/me/deletion-request", headers=auth_header(tok))
        assert resp.status_code == 200
