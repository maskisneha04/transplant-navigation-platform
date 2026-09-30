import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PreferenceInput(BaseModel):
    preference_key: str = Field(max_length=100)
    preference_value: str = Field(max_length=255)


class CaseCreateRequest(BaseModel):
    transplant_type: str
    location_city: str | None = Field(default=None, max_length=100)
    location_state: str | None = Field(default=None, max_length=100)
    preferred_region: str | None = Field(default=None, max_length=100)
    required_services: list[str] | None = None
    logistics_preferences: dict | None = None
    case_description: str | None = Field(default=None, max_length=2000)
    preferences: list[PreferenceInput] | None = None

    @field_validator("transplant_type")
    @classmethod
    def validate_transplant_type(cls, v: str) -> str:
        from app.models.transplant_case import TransplantType

        try:
            TransplantType(v.upper())
        except ValueError:
            allowed = ", ".join(t.value for t in TransplantType)
            raise ValueError(f"transplant_type must be one of: {allowed}")
        return v.upper()


class CaseUpdateRequest(BaseModel):
    """Patients may edit case details only while the case is still early-stage (enforced in the service)."""
    location_city: str | None = Field(default=None, max_length=100)
    location_state: str | None = Field(default=None, max_length=100)
    preferred_region: str | None = Field(default=None, max_length=100)
    required_services: list[str] | None = None
    logistics_preferences: dict | None = None
    case_description: str | None = Field(default=None, max_length=2000)


class StatusTransitionRequest(BaseModel):
    new_status: str
    reason: str | None = Field(default=None, max_length=1000)


class PreferenceResponse(BaseModel):
    preference_key: str
    preference_value: str

    model_config = {"from_attributes": True}


class CaseResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    transplant_type: str
    location_city: str | None
    location_state: str | None
    preferred_region: str | None
    required_services: list[str] | None
    logistics_preferences: dict | None
    case_description: str | None
    status: str
    assigned_coordinator_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseListItemResponse(BaseModel):
    id: uuid.UUID
    transplant_type: str
    status: str
    location_city: str | None
    location_state: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseTimelineEntryResponse(BaseModel):
    id: uuid.UUID
    from_status: str | None
    to_status: str
    changed_by: uuid.UUID
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
