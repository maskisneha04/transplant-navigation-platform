import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Patient(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Extended profile for users with the 'patient' role. Created in Phase 2 flows."""
    __tablename__ = "patients"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    consent_acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="patient")  # noqa: F821
