import time
from pathlib import Path
from typing import Optional
from faster_whisper import WhisperModel

from app.config import settings

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
    Transcrit un fichier audio avec faster-whisper + diarisation pyannote.
    Retourne : text, segments, language, duration, processing_time
    """
    model = get_model()
    start = time.time()

    # ── Étape 1 : Transcription ───────────────────────────────────────────────
    raw_segments, info = model.transcribe(
        audio_path,
        language="fr",
        beam_size=5,
        word_timestamps=False,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )
    whisper_segments = list(raw_segments)

    # ── Étape 2 : Diarisation ────────────────────────────────────────────────
    diarized_segments = []
    diarized_text = ""

    if settings.hf_token:
        try:
            from app.services.diarization import (
                diarize,
                assign_speakers_to_segments,
                format_diarized_text,
            )
            print("[Whisper] Lancement de la diarisation...")
            dia_segments = diarize(audio_path)
            diarized_segments = assign_speakers_to_segments(whisper_segments, dia_segments)
            diarized_text = format_diarized_text(diarized_segments)
            print("[Whisper] Diarisation terminée.")
        except Exception as exc:
            print(f"[Whisper] Diarisation échouée ({exc}), transcription simple utilisée.")

    # ── Texte brut (fallback ou complément) ──────────────────────────────────
    plain_text = " ".join(s.text.strip() for s in whisper_segments)
    final_text = diarized_text if diarized_text else plain_text

    processing_time = time.time() - start

    return {
        "text": final_text,
        "segments": diarized_segments,
        "language_detected": info.language,
        "duration_seconds": info.duration,
        "processing_time_seconds": round(processing_time, 2),
    }
