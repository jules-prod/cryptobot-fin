# Déploiement local

Faire tourner la stack en local, pour le développement et les démos.
Tout est piloté depuis le **`Makefile`** à la racine (`make help` pour la liste complète).

## Pré-requis

```bash
bash ops/setup.sh        # installe les dépendances (multi-OS) + .venv + .env
```

## Option A — Docker (recommandé)

Stack complète (API + Frontend + MLflow + observabilité) :

```bash
make docker              # docker compose up --build
make docker-stop         # docker compose down
make docker-logs         # logs en temps réel
```

| Service | URL |
|---|---|
| API REST | http://localhost:8000/docs |
| Frontend | http://localhost:8501 |
| MLflow | http://localhost:5001 |

## Option B — Sans Docker (processus locaux)

```bash
make run                 # API FastAPI + Streamlit (SQLite par défaut)
make run DB=postgres     # idem avec PostgreSQL (POSTGRES_URL dans .env)
make run-all             # API + MLflow + Streamlit en un seul processus
make mlflow              # MLflow seul (port 5001)
make stop                # arrête l'API lancée en arrière-plan
```

## Données & base

```bash
make collect             # collecte OHLCV incrémentale
make tests               # suite pytest
make db-check            # vérifie la connexion DB active
```

> Les trois cibles de déploiement du projet :
> - **local** → ce dossier (`Makefile` + `docker compose`)
> - **free-cloud** → `../free-cloud/` (Render + Supabase, référence)
> - **prod VPS** → `infra/` (Ansible + `docker compose`, déploiement réel)
