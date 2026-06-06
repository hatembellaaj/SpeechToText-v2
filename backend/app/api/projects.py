"""
Endpoints PROFILER — Projets, Profils, Lots (Batches), Statistiques
"""
import uuid
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.project import Project, Profile
from app.models.batch import Batch
from app.models.analysis import TranscriptionAnalysis

router = APIRouter(prefix="/api/projects", tags=["projects"])


# ── Schémas Pydantic ─────────────────────────────────────────────────────────

class ProfileCreate(BaseModel):
    name: str
    description: str
    keywords: Optional[str] = None
    order: int = 0
    color: str = "#6B7280"
    is_neutral: bool = False


class ProfileResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    keywords: Optional[str]
    order: int
    color: str
    is_neutral: bool

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str
    brand: str
    description: Optional[str] = None
    profiles: list[ProfileCreate] = []


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    brand: str
    description: Optional[str]
    profiles: list[ProfileResponse]
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source: Optional[str] = None
    transcription_ids: list[uuid.UUID] = []


class BatchResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: Optional[str]
    source: Optional[str]
    created_at: datetime
    transcription_count: int = 0

    model_config = {"from_attributes": True}


# ── Projets ───────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        id=uuid.uuid4(),
        name=data.name,
        brand=data.brand,
        description=data.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(project)
    db.flush()

    for p in data.profiles:
        profile = Profile(
            id=uuid.uuid4(),
            project_id=project.id,
            **p.model_dump(),
        )
        db.add(profile)

    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    db.delete(project)
    db.commit()


# ── Profils ───────────────────────────────────────────────────────────────────

@router.post("/{project_id}/profiles", response_model=ProfileResponse, status_code=201)
def add_profile(project_id: uuid.UUID, data: ProfileCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    profile = Profile(id=uuid.uuid4(), project_id=project_id, **data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{project_id}/profiles/{profile_id}", status_code=204)
def delete_profile(project_id: uuid.UUID, profile_id: uuid.UUID, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(
        Profile.id == profile_id, Profile.project_id == project_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil introuvable")
    db.delete(profile)
    db.commit()


# ── Lots (Batches) ────────────────────────────────────────────────────────────

@router.get("/{project_id}/batches", response_model=list[BatchResponse])
def list_batches(project_id: uuid.UUID, db: Session = Depends(get_db)):
    batches = db.query(Batch).filter(Batch.project_id == project_id).order_by(Batch.created_at.desc()).all()
    result = []
    for b in batches:
        result.append(BatchResponse(
            id=b.id,
            project_id=b.project_id,
            name=b.name,
            description=b.description,
            source=b.source,
            created_at=b.created_at,
            transcription_count=len(b.transcriptions),
        ))
    return result


@router.post("/{project_id}/batches", response_model=BatchResponse, status_code=201)
def create_batch(project_id: uuid.UUID, data: BatchCreate, db: Session = Depends(get_db)):
    from app.models.transcription import Transcription
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    batch = Batch(
        id=uuid.uuid4(),
        project_id=project_id,
        name=data.name,
        description=data.description,
        source=data.source,
        created_at=datetime.utcnow(),
    )
    db.add(batch)
    db.flush()

    for tid in data.transcription_ids:
        t = db.query(Transcription).filter(Transcription.id == tid).first()
        if t:
            batch.transcriptions.append(t)

    db.commit()
    db.refresh(batch)
    return BatchResponse(
        id=batch.id,
        project_id=batch.project_id,
        name=batch.name,
        description=batch.description,
        source=batch.source,
        created_at=batch.created_at,
        transcription_count=len(batch.transcriptions),
    )


# ── Statistiques agrégées ─────────────────────────────────────────────────────

@router.get("/{project_id}/stats")
def get_project_stats(project_id: uuid.UUID, batch_id: Optional[uuid.UUID] = None, db: Session = Depends(get_db)):
    """
    Répartition des profils en % pour un projet (ou un lot spécifique).
    Retourne aussi les clusters les plus fréquents et le score moyen de satisfaction.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    # Récupérer les analyses du projet (ou du lot)
    query = db.query(TranscriptionAnalysis).filter(
        TranscriptionAnalysis.project_id == project_id,
        TranscriptionAnalysis.status == "completed",
    )

    if batch_id:
        from app.models.batch import batch_transcriptions
        batch_trans_ids = db.execute(
            batch_transcriptions.select().where(batch_transcriptions.c.batch_id == batch_id)
        ).fetchall()
        trans_ids = [r[1] for r in batch_trans_ids]
        query = query.filter(TranscriptionAnalysis.transcription_id.in_(trans_ids))

    analyses = query.all()
    total = len(analyses)

    if total == 0:
        return {"total": 0, "profiles": [], "clusters": [], "satisfaction_avg": None}

    # Répartition des profils
    profile_counts: dict[str, int] = {}
    profile_names: dict[str, str] = {}
    profile_colors: dict[str, str] = {}

    for a in analyses:
        if a.profile_id:
            pid = str(a.profile_id)
            profile_counts[pid] = profile_counts.get(pid, 0) + 1
            if pid not in profile_names and a.profile:
                profile_names[pid] = a.profile.name
                profile_colors[pid] = a.profile.color

    profiles_stats = [
        {
            "profile_id": pid,
            "name": profile_names.get(pid, "Inconnu"),
            "color": profile_colors.get(pid, "#6B7280"),
            "count": count,
            "percentage": round(count / total * 100, 1),
        }
        for pid, count in sorted(profile_counts.items(), key=lambda x: -x[1])
    ]

    # Non catégorisés
    no_profile = total - sum(profile_counts.values())
    if no_profile > 0:
        profiles_stats.append({
            "profile_id": None,
            "name": "Non catégorisé",
            "color": "#9CA3AF",
            "count": no_profile,
            "percentage": round(no_profile / total * 100, 1),
        })

    # Score satisfaction moyen
    scores = [a.satisfaction_score for a in analyses if a.satisfaction_score is not None]
    satisfaction_avg = round(sum(scores) / len(scores), 1) if scores else None

    # Clusters les plus fréquents
    cluster_counts: dict[str, dict] = {}
    for a in analyses:
        if a.clusters:
            try:
                clusters = json.loads(a.clusters)
                for c in clusters:
                    name = c.get("name", "")
                    if name not in cluster_counts:
                        cluster_counts[name] = {"count": 0, "sentiments": {"+": 0, "neutre": 0, "-": 0}}
                    cluster_counts[name]["count"] += 1
                    s = c.get("sentiment", "neutre")
                    cluster_counts[name]["sentiments"][s] = cluster_counts[name]["sentiments"].get(s, 0) + 1
            except Exception:
                pass

    clusters_stats = sorted(
        [{"name": n, **v} for n, v in cluster_counts.items()],
        key=lambda x: -x["count"]
    )[:10]  # Top 10

    return {
        "total": total,
        "profiles": profiles_stats,
        "clusters": clusters_stats,
        "satisfaction_avg": satisfaction_avg,
    }
