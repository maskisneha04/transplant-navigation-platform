import enum

from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class RoleName(str, enum.Enum):
    patient = "patient"
    coordinator = "coordinator"
    hospital_admin = "hospital_admin"
    system_admin = "system_admin"


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    name: Mapped[RoleName] = mapped_column(SAEnum(RoleName, name="role_name"), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="role")  # noqa: F821
