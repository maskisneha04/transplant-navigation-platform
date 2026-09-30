"""
Seeds the 4 fixed roles (patient, coordinator, hospital_admin, system_admin).
Run once after the first migration. Safe to re-run (skips roles that already exist).

Usage:
    python scripts/seed_roles.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.session import SessionLocal
from app.models.role import Role, RoleName


def run():
    db = SessionLocal()
    try:
        existing = {r.name for r in db.query(Role).all()}
        created = []
        for role_name in RoleName:
            if role_name not in existing:
                db.add(Role(name=role_name, description=f"{role_name.value.replace('_', ' ').title()} role"))
                created.append(role_name.value)
        db.commit()
        if created:
            print(f"Created roles: {', '.join(created)}")
        else:
            print("All roles already exist — nothing to do.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
