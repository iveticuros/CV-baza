"""Create first admin user: python scripts/bootstrap_admin.py admin@example.com 'SecurePass123!' 'Admin Name'"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.constants import ROLE_ADMIN
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash


def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: python scripts/bootstrap_admin.py <email> <password> <name>")
        sys.exit(1)
    email, password, name = sys.argv[1], sys.argv[2], sys.argv[3]
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print("User exists.")
            return
        u = User(
            name=name,
            email=email,
            role=ROLE_ADMIN,
            hashed_password=get_password_hash(password),
            is_active=True,
            email_verified=True,
            admin_approved=True,
            failed_login_attempts=0,
        )
        db.add(u)
        db.commit()
        print("Admin created:", email)
    finally:
        db.close()


if __name__ == "__main__":
    main()
