import uuid

from pydantic import BaseModel


class RecommendationExplanation(BaseModel):
    feature: str
    contribution: float
    reason: str


class CentreRecommendationResponse(BaseModel):
    centre_id: uuid.UUID
    centre_name: str
    city: str | None = None
    district: str | None = None
    state: str | None = None

    score: float
    rank: int

    explanations: list[RecommendationExplanation]

    verification_status: str
    data_source: str | None = None
    source_record_id: int | None = None
    source_dataset_version: str | None = None