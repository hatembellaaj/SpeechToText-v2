from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api.routes import health, transcriptions

# Création des tables (en dev — en prod, utiliser Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes (préfixe /api pour nginx)
app.include_router(health.router, prefix="/api")
app.include_router(transcriptions.router, prefix="/api")
