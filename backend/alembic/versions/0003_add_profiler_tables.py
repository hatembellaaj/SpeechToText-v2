"""Add PROFILER tables: projects, profiles, batches, analyses

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-03 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── projects ──────────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ── profiles ──────────────────────────────────────────────────────────────
    op.create_table(
        "profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("order", sa.Integer(), default=0),
        sa.Column("color", sa.String(20), default="#6B7280"),
        sa.Column("is_neutral", sa.Boolean(), default=False),
    )
    op.create_index("ix_profiles_project_id", "profiles", ["project_id"])

    # ── batches ───────────────────────────────────────────────────────────────
    op.create_table(
        "batches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_batches_project_id", "batches", ["project_id"])

    # ── batch_transcriptions (many-to-many) ───────────────────────────────────
    op.create_table(
        "batch_transcriptions",
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("batches.id"), primary_key=True),
        sa.Column("transcription_id", UUID(as_uuid=True), sa.ForeignKey("transcriptions.id"), primary_key=True),
    )

    # ── transcription_analyses ────────────────────────────────────────────────
    op.create_table(
        "transcription_analyses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("transcription_id", UUID(as_uuid=True), sa.ForeignKey("transcriptions.id"), nullable=False),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("profile_id", UUID(as_uuid=True), sa.ForeignKey("profiles.id"), nullable=True),
        sa.Column("profile_confidence", sa.Float(), nullable=True),
        sa.Column("profile_reasoning", sa.Text(), nullable=True),
        sa.Column("clusters", sa.Text(), nullable=True),
        sa.Column("satisfaction_score", sa.Float(), nullable=True),
        sa.Column("satisfaction_reasoning", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_analyses_transcription_id", "transcription_analyses", ["transcription_id"])
    op.create_index("ix_analyses_project_id", "transcription_analyses", ["project_id"])

    # ── project_id sur transcriptions (optionnel à l'upload) ──────────────────
    op.add_column("transcriptions", sa.Column(
        "project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=True
    ))


def downgrade() -> None:
    op.drop_column("transcriptions", "project_id")
    op.drop_table("transcription_analyses")
    op.drop_table("batch_transcriptions")
    op.drop_table("batches")
    op.drop_table("profiles")
    op.drop_table("projects")
