"""
REAL (Phase 2): transplant case management. The scaffolding note from Phase 1
no longer applies to this file — these tables now back a working API.
"""
import enum
import uuid

from sqlalchemy import String, Text, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class TransplantType(str, enum.Enum):
    KIDNEY = "KIDNEY"
    LIVER = "LIVER"
    HEART = "HEART"
    LUNG = "LUNG"
    CORNEAL = "CORNEAL"
    BONE_MARROW = "BONE_MARROW"


class CaseStatus(str, enum.Enum):
    """
    Controlled case lifecycle (Phase 2). Transitions are enforced centrally
    in app/services/case_service.py — never mutate `status` directly.
    """
    NEW = "NEW"
    DOCUMENT_COLLECTION = "DOCUMENT_COLLECTION"
    UNDER_REVIEW = "UNDER_REVIEW"
    COORDINATOR_REVIEW = "COORDINATOR_REVIEW"
    CENTRE_REVIEW = "CENTRE_REVIEW"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TransplantCase(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "transplant_cases"

    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    transplant_type: Mapped[TransplantType] = mapped_column(SAEnum(TransplantType, name="transplant_type"), nullable=False)
    location_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required_services: Mapped[list | None] = mapped_column(JSON, nullable=True)
    logistics_preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    case_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CaseStatus] = mapped_column(SAEnum(CaseStatus, name="case_status"), default=CaseStatus.NEW, nullable=False, index=True)
    assigned_coordinator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


class PatientPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "patient_preferences"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_cases.id"), nullable=False, index=True)
    preference_key: Mapped[str] = mapped_column(String(100), nullable=False)
    preference_value: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[float | None] = mapped_column(nullable=True)


class CaseStatusHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "case_status_history"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_cases.id"), nullable=False, index=True)
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
