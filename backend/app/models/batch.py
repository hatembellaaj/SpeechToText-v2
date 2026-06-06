import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

# Table d'association Batch ↔ Transcription (many-to-many)
batch_transcriptions = Table(
    "batch_transcriptions",
    Base.metadata,
    Column("batch_id", UUID(as_uuid=True), ForeignKey("batches.id"), primary_key=True),
    Column("transcription_id", UUID(as_uuid=True), ForeignKey("transcriptions.id"), primary_key=True),
)


class Batch(Base):
    """Lot d'audios regroupés pour analyse statistique agrégée."""
    __tablename__ = "batches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)  # ex: "centre-appels-lyon"

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    project: Mapped["Project"] = relationship("Project", back_populates="batches")  # type: ignore
    transcriptions: Mapped[list] = relationship(
        "Transcription",
        secondary=batch_transcriptions,
        backref="batches",
    )
