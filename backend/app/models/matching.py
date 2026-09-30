"""SCAFFOLDING (Phase 1) — recommendation engine built in Phase 3-5."""
import uuid
from datetime import datetime

from sqlalchemy import Float, Integer, Boolean, Text, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class MatchingResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "matching_results"
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_cases.id"), nullable=False)
    centre_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_centres.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=True)
    is_override: Mapped[bool] = mapped_column(Boolean, default=False)
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class MatchingFeature(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "matching_features"
    matching_result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matching_results.id"), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contribution_value: Mapped[float] = mapped_column(Float, nullable=False)
    raw_value: Mapped[float | None] = mapped_column(Float, nullable=True)
