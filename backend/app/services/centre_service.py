import uuid

from sqlalchemy import cast, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.models.centre import TransplantCentre


def list_centres(
    db: Session,
    *,
    search: str | None = None,
    state: str | None = None,
    transplant_type: str | None = None,
    registration_type: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[TransplantCentre]:
    query = select(TransplantCentre)

    if search:
        query = query.where(
            TransplantCentre.name.ilike(f"%{search.strip()}%")
        )

    if state:
        query = query.where(
            TransplantCentre.state.ilike(state.strip())
        )

    if registration_type:
        query = query.where(
            TransplantCentre.registration_type.ilike(
                registration_type.strip()
            )
        )

    if transplant_type:
        query = query.where(
            cast(
                TransplantCentre.transplant_types,
                JSONB,
            ).contains(
                [transplant_type.strip()]
            )
        )
    

    query = (
        query
        .order_by(TransplantCentre.name.asc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(query).all())


def get_centre(
    db: Session,
    centre_id: uuid.UUID,
) -> TransplantCentre | None:
    query = select(TransplantCentre).where(
        TransplantCentre.id == centre_id
    )

    return db.scalar(query)