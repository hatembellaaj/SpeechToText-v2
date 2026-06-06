import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TranscriptionAnalysis(Base):
    """
    Résultat de l'analyse LLM d'une transcription dans le contexte d'un projet.
    Couvre Lot 1 (profil) et Lot 2 (clusters/sentiment/satisfaction).
    """
    __tablename__ = "transcription_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    transcription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transcriptions.id"), nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )

    # ── Lot 1 : Profil ───────────────────────────────────────────────────────
    profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True
    )
    profile_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0.0–1.0
    profile_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Lot 2 : Clusters & sentiment ─────────────────────────────────────────
    # JSON : [{"name": "Prix", "sentiment": "+", "sub_clusters": [{"name": "tarif élevé", "sentiment": "-"}]}]
    clusters: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Score de satisfaction global (0–10), généré par IA ou donné en fin d'appel
    satisfaction_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    satisfaction_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Statut de l'analyse
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|processing|completed|failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relations
    transcription: Mapped["Transcription"] = relationship("Transcription")  # type: ignore
    project: Mapped["Project"] = relationship("Project")  # type: ignore
    profile: Mapped["Profile"] = relationship("Profile")  # type: ignore
