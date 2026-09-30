"""SCAFFOLDING (Phase 1) — populated for real starting in Phase 3-4 (model_versions)
and used for configurable recommendation weights / thresholds (system_settings)."""
from datetime import datetime

from sqlalchemy import String, JSON, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class ModelVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "model_versions"

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    version_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    training_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    feature_list: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dataset_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)


class SystemSetting(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
