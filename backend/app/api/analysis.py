"""
Endpoints PROFILER — Déclenchement et consultation des analyses
"""
import uuid
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.analysis import TranscriptionAnalysis
from app.models.project import Project, Profile
from app.models.transcription import Transcription, TranscriptionStatus

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    transcription_id: uuid.UUID
    project_id: uuid.UUID


class AnalysisResponse(BaseModel):
    id: uuid.UUID
    transcription_id: uuid.UUID
    project_id: uuid.UUID
    status: str
    profile_id: Optional[uuid.UUID]
    profile_name: Optional[str] = None
    profile_color: Optional[str] = None
    profile_confidence: Optional[float]
    profile_reasoning: Optional[str]
    clusters: Optional[list] = None
    satisfaction_score: Optional[float]
    satisfaction_reasoning: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


def _run_analysis(analysis_id: uuid.UUID, db: Session):
    """Exécute l'analyse LLM en arrière-plan."""
    from app.services.analysis import run_full_analysis

    analysis = db.query(TranscriptionAnalysis).filter(
        TranscriptionAnalysis.id == analysis_id
    ).first()
    if not analysis:
        return

    try:
        analysis.status = "processing"
        analysis.updated_at = datetime.utcnow()
        db.commit()

        # Récupérer la transcription
        transcription = db.query(Transcription).filter(
            Transcription.id == analysis.transcription_id
        ).first()
        if not transcription or not transcription.text:
            raise ValueError("Transcription sans texte")

        # Récupérer les profils du projet
        profiles = db.query(Profile).filter(
            Profile.project_id == analysis.project_id
        ).order_by(Profile.order).all()

        profiles_data = [
            {"id": str(p.id), "name": p.name, "description": p.description, "is_neutral": p.is_neutral}
            for p in profiles
        ]

        # Lancer l'analyse
        result = run_full_analysis(transcription.text, profiles_data)

        # Sauvegarder les résultats
        if "profile_id" in result:
            analysis.profile_id = uuid.UUID(result["profile_id"]) if result["profile_id"] else None
            analysis.profile_confidence = result.get("confidence")
            analysis.profile_reasoning = result.get("reasoning")

        if "clusters" in result:
            analysis.clusters = json.dumps(result["clusters"], ensure_ascii=False)
            analysis.satisfaction_score = result.get("satisfaction_score")
            analysis.satisfaction_reasoning = result.get("satisfaction_reasoning")

        analysis.status = "completed"
        analysis.updated_at = datetime.utcnow()
        db.commit()

        print(f"[Analysis] ✓ Analyse {analysis_id} terminée")

    except Exception as exc:
        analysis.status = "failed"
        analysis.error_message = str(exc)
        analysis.updated_at = datetime.utcnow()
        db.commit()
        print(f"[Analysis] ✗ Erreur analyse {analysis_id}: {exc}")


@router.post("", response_model=AnalysisResponse, status_code=202)
def trigger_analysis(
    data: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Déclenche l'analyse d'une transcription dans le contexte d'un projet."""
    # Vérifications
    transcription = db.query(Transcription).filter(
        Transcription.id == data.transcription_id
    ).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription introuvable")
    if transcription.status != TranscriptionStatus.completed:
        raise HTTPException(status_code=400, detail="La transcription n'est pas encore terminée")

    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    # Créer (ou réinitialiser) l'entrée d'analyse
    existing = db.query(TranscriptionAnalysis).filter(
        TranscriptionAnalysis.transcription_id == data.transcription_id,
        TranscriptionAnalysis.project_id == data.project_id,
    ).first()

    if existing:
        existing.status = "pending"
        existing.error_message = None
        existing.updated_at = datetime.utcnow()
        analysis = existing
    else:
        analysis = TranscriptionAnalysis(
            id=uuid.uuid4(),
            transcription_id=data.transcription_id,
            project_id=data.project_id,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(analysis)

    db.commit()
    db.refresh(analysis)

    # Lancer en arrière-plan
    background_tasks.add_task(_run_analysis, analysis.id, db)

    return _build_response(analysis, db)


@router.get("/transcription/{transcription_id}", response_model=list[AnalysisResponse])
def get_analyses_for_transcription(transcription_id: uuid.UUID, db: Session = Depends(get_db)):
    analyses = db.query(TranscriptionAnalysis).filter(
        TranscriptionAnalysis.transcription_id == transcription_id
    ).all()
    return [_build_response(a, db) for a in analyses]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: uuid.UUID, db: Session = Depends(get_db)):
    a = db.query(TranscriptionAnalysis).filter(TranscriptionAnalysis.id == analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analyse introuvable")
    return _build_response(a, db)


def _build_response(a: TranscriptionAnalysis, db: Session) -> AnalysisResponse:
    profile_name = None
    profile_color = None
    if a.profile_id:
        p = db.query(Profile).filter(Profile.id == a.profile_id).first()
        if p:
            profile_name = p.name
            profile_color = p.color

    clusters = None
    if a.clusters:
        try:
            clusters = json.loads(a.clusters)
        except Exception:
            pass

    return AnalysisResponse(
        id=a.id,
        transcription_id=a.transcription_id,
        project_id=a.project_id,
        status=a.status,
        profile_id=a.profile_id,
        profile_name=profile_name,
        profile_color=profile_color,
        profile_confidence=a.profile_confidence,
        profile_reasoning=a.profile_reasoning,
        clusters=clusters,
        satisfaction_score=a.satisfaction_score,
        satisfaction_reasoning=a.satisfaction_reasoning,
        error_message=a.error_message,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )
