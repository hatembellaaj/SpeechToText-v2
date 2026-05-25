from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "SpeechToText Thermor"
    environment: str = "development"
    secret_key: str = "changeme"

    # Base de données
    database_url: str = "postgresql://stt_user:changeme@postgres:5432/stt_db"

    # Redis / Celery
    redis_url: str = "redis://redis:6379/0"

    # Fichiers
    upload_dir: str = "/app/uploads"
    model_dir: str = "/app/models"
    max_upload_size_mb: int = 500

    # Whisper
    whisper_model: str = "large-v3"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    # HuggingFace (diarisation)
    hf_token: str = ""

    # CORS
    allowed_origins: str = "http://localhost,http://localhost:80,http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "protected_namespaces": (),
    }


settings = Settings()
