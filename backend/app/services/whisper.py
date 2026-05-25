import time
from pathlib import Path
from typing import Optional
from faster_whisper import WhisperModel

from app.config import settings

# Instance singleton du modèle (chargé une seule fois par process worker)
_model: Optional[WhisperModel] = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        print(f"[Whisper] Chargement du modèle {settings.whisper_model}...")
        _model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
            download_root=settings.model_dir,
        )
        print(f"[Whisper] Modèle {settings.whisper_model} chargé.")
    return _model


def transcribe_file(audio_path: str) -> dict:
    """
    Transcrit un fichier audio avec faster-whisper.
    Retourne un dict avec : text, language, duration, processing_time
    """
    model = get_model()
    start = time.time()

    segments, info = model.transcribe(
        audio_path,
        language="fr",
        beam_size=5,
        vad_filter=True,          # Filtre les silences
        vad_parameters=dict(
            min_silence_duration_ms=500
        ),
    )

    # Assemblage des segments en texte complet
    full_text = " ".join(segment.text.strip() for segment in segments)

    processing_time = time.time() - start

    return {
        "text": full_text,
        "language_detected": info.language,
        "duration_seconds": info.duration,
        "processing_time_seconds": round(processing_time, 2),
    }
