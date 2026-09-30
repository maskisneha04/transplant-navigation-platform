from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.services import auth_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, payload.email, payload.password, payload.role)
    return UserResponse(id=user.id, email=user.email, role=user.role.name.value, is_active=user.is_active)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    tokens = auth_service.authenticate_and_issue_tokens(db, payload.email, payload.password)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    tokens = auth_service.refresh_access_token(db, payload.refresh_token)
    return TokenResponse(**tokens)


@router.post("/logout", status_code=204)
def logout():
    # Stateless JWT: real invalidation (token blocklist in Redis) is added
    # when the realtime/Redis layer is built in Phase 9. For now the frontend
    # simply discards its stored tokens.
    return None


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role.name.value,
        is_active=current_user.is_active,
    )
