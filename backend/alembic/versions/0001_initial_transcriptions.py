"""Initial transcriptions table

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transcriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "processing", "completed", "failed",
                name="transcriptionstatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("language_detected", sa.String(10), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("processing_time_seconds", sa.Float(), nullable=True),
        sa.Column("whisper_model", sa.String(50), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_transcriptions_status", "transcriptions", ["status"])
    op.create_index("ix_transcriptions_created_at", "transcriptions", ["created_at"])


def downgrade() -> None:
    op.drop_table("transcriptions")
    op.execute("DROP TYPE IF EXISTS transcriptionstatus")
