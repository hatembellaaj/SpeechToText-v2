FROM python:3.11-slim

# Dépendances système pour faster-whisper et ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Dossiers pour uploads et modèles (montés en volumes)
RUN mkdir -p /app/uploads /app/models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
