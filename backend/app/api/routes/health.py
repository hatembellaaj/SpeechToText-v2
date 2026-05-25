from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "model": settings.whisper_model,
        "environment": settings.environment,
    }
