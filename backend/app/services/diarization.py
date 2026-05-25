from typing import Optional
from app.config import settings

_pipeline = None


def get_diarization_pipeline():
    global _pipeline
    if _pipeline is None:
        from pyannote.audio import Pipeline
        print("[Diarisation] Chargement du pipeline pyannote...")
        _pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=settings.hf_token or True,
        )
        print("[Diarisation] Pipeline chargé.")
    return _pipeline


def diarize(audio_path: str) -> list[dict]:
    """
    Identifie les segments de parole par interlocuteur.
    Retourne une liste de {start, end, speaker}.
    """
    pipeline = get_diarization_pipeline()
    diarization = pipeline(audio_path)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": round(turn.start, 3),
            "end": round(turn.end, 3),
            "speaker": speaker,
        })
    return segments


def assign_speakers_to_segments(whisper_segments: list, diarization_segments: list) -> list[dict]:
    """
    Associe chaque segment Whisper au locuteur correspondant
    en cherchant le locuteur dominant sur la durée du segment.
    """
    result = []
    for seg in whisper_segments:
        seg_start = seg.start
        seg_end = seg.end
        seg_mid = (seg_start + seg_end) / 2

        # Cherche d'abord par midpoint
        speaker = None
        for d in diarization_segments:
            if d["start"] <= seg_mid <= d["end"]:
                speaker = d["speaker"]
                break

        # Fallback : plus grand overlap
        if speaker is None:
            best_overlap = 0.0
            for d in diarization_segments:
                overlap = min(seg_end, d["end"]) - max(seg_start, d["start"])
                if overlap > best_overlap:
                    best_overlap = overlap
                    speaker = d["speaker"]

        result.append({
            "speaker": speaker or "SPEAKER_00",
            "start": round(seg_start, 3),
            "end": round(seg_end, 3),
            "text": seg.text.strip(),
        })

    return result


def format_diarized_text(segments: list[dict]) -> str:
    """
    Formate les segments en texte lisible avec étiquettes interlocuteurs.
    Regroupe les segments consécutifs du même locuteur.
    """
    if not segments:
        return ""

    # Normalise les noms SPEAKER_00 → Intervenant 1
    speaker_map: dict[str, str] = {}
    counter = 1
    for seg in segments:
        sp = seg.get("speaker", "SPEAKER_00")
        if sp not in speaker_map:
            speaker_map[sp] = f"Intervenant {counter}"
            counter += 1

    # Regroupe les segments consécutifs du même locuteur
    lines = []
    current_speaker = None
    current_texts = []

    for seg in segments:
        sp = speaker_map.get(seg.get("speaker", ""), "Intervenant ?")
        text = seg.get("text", "").strip()
        if not text:
            continue
        if sp == current_speaker:
            current_texts.append(text)
        else:
            if current_speaker and current_texts:
                lines.append(f"[{current_speaker}] {' '.join(current_texts)}")
            current_speaker = sp
            current_texts = [text]

    if current_speaker and current_texts:
        lines.append(f"[{current_speaker}] {' '.join(current_texts)}")

    return "\n".join(lines)
