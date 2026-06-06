import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)  # ex: "Thermor"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    profiles: Mapped[list["Profile"]] = relationship(
        "Profile", back_populates="project", cascade="all, delete-orphan",
        order_by="Profile.order"
    )
    batches: Mapped[list["Batch"]] = relationship(
        "Batch", back_populates="project", cascade="all, delete-orphan"
    )


class Profile(Base):
    """Profil comportemental d'un client (6 + 1 neutre par projet)."""
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)  # utilisé dans le prompt LLM
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)  # mots-clés indicatifs JSON
    order: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str] = mapped_column(String(20), default="#6B7280")  # couleur UI
    is_neutral: Mapped[bool] = mapped_column(Boolean, default=False)  # 7ème profil "Non catégorisé"

    project: Mapped["Project"] = relationship("Project", back_populates="profiles")
