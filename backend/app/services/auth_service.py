from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import user_repository
from app.security.hashing import hash_password, verify_password
from app.security.jwt import create_access_token, create_refresh_token, decode_token, JWTError
from app.services import audit_service
from app.models.user import User


ALLOWED_SELF_REGISTER_ROLES = {"patient"}
# Coordinator / hospital_admin / system_admin accounts are meant to be created
# through the admin-management API (built in a later phase) or scripts/create_admin.py,
# not open self-registration — this keeps admin access controlled, per the spec.


def register_user(db: Session, email: str, password: str, role: str) -> User:
    if role not in ALLOWED_SELF_REGISTER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Self-registration is only available for the 'patient' role. "
            "Other roles are provisioned by a system administrator.",
        )

    if user_repository.get_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists."
        )

    role_row = user_repository.get_role_by_name(db, role)
    if role_row is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown role.")

    user = user_repository.create_user(db, email=email, password_hash=hash_password(password), role_id=role_row.id)
    audit_service.log_action(db, action="USER_REGISTERED", user_id=user.id, entity_type="user", entity_id=user.id, metadata={"email": email, "role": role})
    return user


def authenticate_and_issue_tokens(db: Session, email: str, password: str) -> dict:
    user = user_repository.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        audit_service.log_action(db, action="LOGIN_FAILED", metadata={"email": email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    audit_service.log_action(db, action="LOGIN_SUCCESS", user_id=user.id, entity_type="user", entity_id=user.id)

    role_name = user.role.name.value
    return {
        "access_token": create_access_token(str(user.id), role_name),
        "refresh_token": create_refresh_token(str(user.id), role_name),
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("wrong token type")
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token.")

    user = user_repository.get_by_id(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    role_name = user.role.name.value
    return {
        "access_token": create_access_token(str(user.id), role_name),
        "refresh_token": create_refresh_token(str(user.id), role_name),
        "token_type": "bearer",
    }
