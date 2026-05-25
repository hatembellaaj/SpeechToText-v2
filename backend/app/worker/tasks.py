import uuid
import json
from datetime import datetime

from celery import Task
from app.worker.celery_app import celery_app
from app.database import SessionLocal
from app.models.transcription import Transcription, TranscriptionStatus
from app.services.whisper import transcribe_file


class TranscribeTask(Task):
    """Tâche avec retry automatique."""
    autoretry_for = (Exception,)
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = 60


@celery_app.task(base=TranscribeTask, bind=True, name="transcribe_audio")
def transcribe_audio(self, transcription_id: str, audio_path: str):
    """
    Tâche Celery principale : transcrit un fichier audio et met à jour la DB.
    """
    db = SessionLocal()
    try:
        t = db.query(Transcription).filter(
            Transcription.id == uuid.UUID(transcription_id)
        ).first()

        if not t:
            raise ValueError(f"Transcription {transcription_id} introuvable en DB")

        # Marquer comme en cours
        t.status = TranscriptionStatus.processing
        t.updated_at = datetime.utcnow()
        db.commit()

        # Lancer la transcription
        result = transcribe_file(audio_path)

        # Mettre à jour avec les résultats
        t.status = TranscriptionStatus.completed
        t.text = result["text"]
        t.segments = json.dumps(result.get("segments") or [], ensure_ascii=False)
        t.language_detected = result["language_detected"]
        t.duration_seconds = result["duration_seconds"]
        t.processing_time_seconds = result["processing_time_seconds"]
        t.updated_at = datetime.utcnow()
        db.commit()

        print(f"[Worker] ✓ Transcription {transcription_id} terminée "
              f"({result['processing_time_seconds']:.1f}s)")

    except Exception as exc:
        # Marquer comme échoué
        if db:
            try:
                t = db.query(Transcription).filter(
                    Transcription.id == uuid.UUID(transcription_id)
                ).first()
                if t:
                    t.status = TranscriptionStatus.failed
                    t.error_message = str(exc)
                    t.updated_at = datetime.utcnow()
                    db.commit()
            except Exception:
                pass

        print(f"[Worker] ✗ Erreur transcription {transcription_id}: {exc}")
        raise self.retry(exc=exc)

    finally:
        db.close()
