import os
import uuid
import shutil
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.transcription import Transcription, TranscriptionStatus
from app.schemas.transcription import (
    TranscriptionResponse,
    TranscriptionListResponse,
    TranscriptionUploadResponse,
)
from app.worker.tasks import transcribe_audio
from app.config import settings

router = APIRouter(prefix="/transcriptions", tags=["transcriptions"])

ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".aac"}


@router.post("/upload", response_model=TranscriptionUploadResponse, status_code=202)
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload un fichier audio et démarre la transcription en arrière-plan."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté : {suffix}. Formats acceptés : {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Vérification taille
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Fichier trop volumineux : {file_size / 1024 / 1024:.1f} MB (max {settings.max_upload_size_mb} MB)",
        )

    # Sauvegarde du fichier
    stored_filename = f"{uuid.uuid4()}{suffix}"
    upload_path = Path(settings.upload_dir) / stored_filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Création de l'entrée en base
    transcription = Transcription(
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_size_bytes=file_size,
        whisper_model=settings.whisper_model,
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)

    # Envoi de la tâche au worker
    transcribe_audio.delay(str(transcription.id), str(upload_path))

    return TranscriptionUploadResponse(
        id=transcription.id,
        original_filename=transcription.original_filename,
        status=transcription.status,
        message="Fichier reçu. Transcription en cours de traitement.",
    )


@router.get("", response_model=TranscriptionListResponse)
def list_transcriptions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[TranscriptionStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Liste l'historique des transcriptions avec pagination et filtres."""
    query = db.query(Transcription)

    if status:
        query = query.filter(Transcription.status == status)

    if search:
        query = query.filter(
            Transcription.original_filename.ilike(f"%{search}%")
            | Transcription.text.ilike(f"%{search}%")
        )

    total = query.count()
    items = (
        query.order_by(desc(Transcription.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return TranscriptionListResponse(total=total, items=items)


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
def get_transcription(transcription_id: uuid.UUID, db: Session = Depends(get_db)):
    """Récupère une transcription par son ID."""
    t = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transcription introuvable")
    return t


@router.get("/{transcription_id}/text", response_class=PlainTextResponse)
def download_text(transcription_id: uuid.UUID, db: Session = Depends(get_db)):
    """Télécharge le texte brut d'une transcription."""
    t = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transcription introuvable")
    if t.status != TranscriptionStatus.completed:
        raise HTTPException(status_code=409, detail="Transcription pas encore terminée")
    return t.text or ""


@router.delete("/{transcription_id}", status_code=204)
def delete_transcription(transcription_id: uuid.UUID, db: Session = Depends(get_db)):
    """Supprime une transcription et son fichier audio."""
    t = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transcription introuvable")

    # Suppression du fichier audio
    audio_path = Path(settings.upload_dir) / t.stored_filename
    if audio_path.exists():
        audio_path.unlink()

    db.delete(t)
    db.commit()
