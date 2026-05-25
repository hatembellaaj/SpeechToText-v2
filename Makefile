.PHONY: help up down restart logs build pull deploy migrate

help:
	@echo "Commandes disponibles :"
	@echo "  make up       — Démarrer tous les services"
	@echo "  make down     — Arrêter tous les services"
	@echo "  make restart  — Redémarrer tous les services"
	@echo "  make build    — Rebuilder les images"
	@echo "  make logs     — Voir les logs (tous les services)"
	@echo "  make logs-api — Voir les logs de l'API"
	@echo "  make logs-worker — Voir les logs du worker"
	@echo "  make migrate  — Appliquer les migrations DB"
	@echo "  make pull     — git pull + rebuild + restart (déploiement)"
	@echo "  make shell-api — Ouvrir un shell dans le conteneur API"
	@echo "  make psql     — Ouvrir psql dans le conteneur PostgreSQL"

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

build:
	docker compose build --no-cache

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-worker:
	docker compose logs -f worker

migrate:
	docker compose exec api alembic upgrade head

shell-api:
	docker compose exec api bash

psql:
	docker compose exec postgres psql -U $${POSTGRES_USER:-stt_user} -d $${POSTGRES_DB:-stt_db}

# ─── Déploiement serveur ────────────────────────────────────────────────────────
# Usage : ssh user@server "cd /opt/stt && make deploy"
deploy:
	git pull origin main
	docker compose build --no-cache
	docker compose up -d
	docker compose exec -T api alembic upgrade head
	@echo "✓ Déploiement terminé"
