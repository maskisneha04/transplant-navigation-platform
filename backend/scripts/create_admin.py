"""
Creates one system_admin account for local development/demo use.
Uses an obviously synthetic email, per the project's data-safety rules.

Usage:
    python scripts/create_admin.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.session import SessionLocal
from app.repositories import user_repository
from app.security.hashing import hash_password

DEMO_ADMIN_EMAIL = "admin.demo@example.com"
DEMO_ADMIN_PASSWORD = "ChangeMe123!"  # noqa: change this after first login in any non-local environment


def run():
    db = SessionLocal()
    try:
        if user_repository.get_by_email(db, DEMO_ADMIN_EMAIL):
            print(f"Admin account already exists: {DEMO_ADMIN_EMAIL}")
            return

        role = user_repository.get_role_by_name(db, "system_admin")
        if role is None:
            print("Roles not seeded yet. Run 'python scripts/seed_roles.py' first.")
            return

        user_repository.create_user(
            db, email=DEMO_ADMIN_EMAIL, password_hash=hash_password(DEMO_ADMIN_PASSWORD), role_id=role.id
        )
        print(f"Created demo system_admin account: {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}")
        print("This is a SYNTHETIC demo account for local development only.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
