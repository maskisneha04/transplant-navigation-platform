from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role, RoleName


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()


def get_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()


def get_role_by_name(db: Session, role_name: str) -> Role | None:
    return db.query(Role).filter(Role.name == RoleName(role_name)).first()


def create_user(db: Session, email: str, password_hash: str, role_id) -> User:
    user = User(email=email, password_hash=password_hash, role_id=role_id, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
