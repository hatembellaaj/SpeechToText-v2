import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.transcription import TranscriptionStatus


class TranscriptionResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    file_size_bytes: Optional[int]
    status: TranscriptionStatus
    text: Optional[str]
    language_detected: Optional[str]
    duration_seconds: Optional[float]
    processing_time_seconds: Optional[float]
    whisper_model: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TranscriptionListResponse(BaseModel):
    total: int
    items: list[TranscriptionResponse]


class TranscriptionUploadResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    status: TranscriptionStatus
    message: str
