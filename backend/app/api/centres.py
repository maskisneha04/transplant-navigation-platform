import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.centre import (
    CentreListItemResponse,
    CentreResponse,
)
from app.services import centre_service


router = APIRouter(
    prefix="/centres",
    tags=["centres"],
)


@router.get(
    "",
    response_model=list[CentreListItemResponse],
)
def list_centres(
    search: str | None = Query(default=None),
    state: str | None = Query(default=None),
    transplant_type: str | None = Query(default=None),
    registration_type: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    centres = centre_service.list_centres(
        db,
        search=search,
        state=state,
        transplant_type=transplant_type,
        registration_type=registration_type,
        skip=skip,
        limit=limit,
    )

    return [
        CentreListItemResponse.model_validate(centre)
        for centre in centres
    ]


@router.get(
    "/{centre_id}",
    response_model=CentreResponse,
)
def get_centre(
    centre_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    centre = centre_service.get_centre(
        db,
        centre_id,
    )

    if centre is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Transplant centre not found",
        )

    return CentreResponse.model_validate(centre)