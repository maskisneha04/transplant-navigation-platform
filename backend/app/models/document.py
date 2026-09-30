"""SCAFFOLDING (Phase 1) — real upload/OCR/classification logic built in Phase 6-7."""
import uuid

from sqlalchemy import String, Float, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class DocumentType(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_types"
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class DocumentChecklist(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_checklists"
    centre_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_centres.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(default=1)


class DocumentRequirement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_requirements"
    checklist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("document_checklists.id"), nullable=False)
    document_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("document_types.id"), nullable=False)
    requirement_level: Mapped[str] = mapped_column(String(20), default="REQUIRED")  # REQUIRED / OPTIONAL


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transplant_cases.id"), nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(nullable=False)
    document_type_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("document_types.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="UPLOADED")
    sha256_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)


class DocumentAnalysis(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_analysis"
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    predicted_type_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("document_types.id"), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extracted_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=True)
    needs_human_review: Mapped[bool] = mapped_column(Boolean, default=False)
