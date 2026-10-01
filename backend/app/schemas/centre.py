import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CentreListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    city: str | None = None
    district: str | None = None
    state: str | None = None
    registration_type: str | None = None
    transplant_types: list[str] | None = None
    verification_status: str
    data_source: str | None = None
    last_verified_at: datetime | None = None


class CentreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    address: str | None = None
    city: str | None = None
    district: str | None = None
    state: str | None = None
    registration_type: str | None = None
    transplant_types: list[str] | None = None
    raw_organ_tissue_type: str | None = None
    details: str | None = None
    website: str | None = None

    capability_score: float | None = None
    logistics_score: float | None = None

    verification_status: str
    data_source: str | None = None
    source_record_id: int | None = None
    source_dataset_version: str | None = None
    last_verified_at: datetime | None = None