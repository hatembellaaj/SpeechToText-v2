from celery import Celery
from app.config import settings

celery_app = Celery(
    "stt_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Paris",
    enable_utc=True,
    # Retry automatique en cas d'erreur transitoire
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Pas de timeout (les transcriptions longues peuvent prendre du temps)
    task_soft_time_limit=None,
    task_time_limit=None,
)
