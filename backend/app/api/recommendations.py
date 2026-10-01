import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.recommendation import CentreRecommendationResponse
from app.services import case_service, recommendation_service


router = APIRouter(
    prefix="/cases",
    tags=["recommendations"],
)


@router.get(
    "/{case_id}/recommendations",
    response_model=list[CentreRecommendationResponse],
)
def get_case_recommendations(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    case = case_service.get_case(
    db,
    user,
    case_id,
)

    return recommendation_service.rank_centres_for_case(
        db,
        case,
    )