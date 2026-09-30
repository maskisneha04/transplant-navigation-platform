"""SCAFFOLDING (Phase 1) — real logic + synthetic dataset built in Phase 3."""
import uuid

from sqlalchemy import String, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class TransplantCentre(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "transplant_centres"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    transplant_types: Mapped[list | None] = mapped_column(JSON, nullable=True)
    capability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    logistics_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="synthetic_demo")
    data_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_verified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CentreCapability(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "centre_capabilities"
    centre_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_centres.id"), nullable=False)
    capability_name: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)


class CentreService(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "centre_services"
    centre_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_centres.id"), nullable=False)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    available: Mapped[bool] = mapped_column(default=True)


class CentreVerification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "centre_verification"
    centre_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_centres.id"), nullable=False)
    verification_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
