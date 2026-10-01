import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.centre import TransplantCentre


def list_centres_for_navigation(
    db: Session,
    *,
    transplant_type: str | None = None,
    state: str | None = None,
) -> list[TransplantCentre]:
    query = select(TransplantCentre)

    if state:
        query = query.where(
            TransplantCentre.state.ilike(state.strip())
        )

    if transplant_type:
        query = query.where(
            TransplantCentre.transplant_types.is_not(None)
        )

    query = query.order_by(TransplantCentre.name.asc())

    return list(db.scalars(query).all())


def get_centre_by_id(
    db: Session,
    centre_id: uuid.UUID,
) -> TransplantCentre | None:
    query = select(TransplantCentre).where(
        TransplantCentre.id == centre_id
    )

    return db.scalar(query)