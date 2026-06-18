# Crypto Bot

Plateforme de collecte, stockage et analyse de données crypto.  
Pipeline ETL multi-exchange → base de données → API REST → dashboard Streamlit + veille actualités + backtesting ML + **paper trading temps réel** + suivi d'expériences MLflow.

## Installation

```bash
bash ops/setup.sh
```

`ops/setup.sh` détecte l'OS et installe les dépendances adaptées :

| OS | Support |
|---|---|
| macOS | Homebrew + libpq |
| Linux (Debian/Ubuntu) | apt — `python3-dev libpq-dev` |
| Linux (RedHat) | yum — `python3-devel postgresql-devel` |
| Linux (Arch / Alpine) | pacman / apk |
| Windows | Non supporté nativement — utiliser WSL2 ou Docker |

Le script vérifie Python 3.10+, crée un `.venv` si nécessaire, installe `requirements.txt` et copie `.env.example` → `.env`.  
Éditez `.env` avec vos clés API avant de lancer les collectes.

## Démarrage rapide

```bash
bash ops/setup.sh                 # Installation (première fois)

# Stack complète via Docker (recommandé) :
docker compose up --build         # API (8000) + Frontend (8501) + MLflow (5001) + observabilité
```

## Commandes

> Par défaut la base est SQLite. Pour PostgreSQL, définir `POSTGRES_URL` (ou `CRYPTO_BOT_DB_URL`) dans `.env`.

### Local (sans Docker)

```bash
# API FastAPI (port 8000)
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Frontend Streamlit (port 8501)
streamlit run src/frontend/app.py

# MLflow seul (port 5001)
mlflow server --host 0.0.0.0 --port 5001 \
  --backend-store-uri sqlite:///mlflow-local.db \
  --default-artifact-root ./mlflow-artifacts --allowed-hosts "*"

# Arrêter l'API lancée en arrière-plan
pkill -f "uvicorn src.api.main:app"
```

### Docker

```bash
docker compose up --build         # Build et démarre tous les services
docker compose down               # Arrête tous les conteneurs
docker compose logs -f            # Logs en temps réel
```

| Service  | URL                        |
|----------|----------------------------|
| API REST | http://localhost:8000/docs |
| Frontend | http://localhost:8501      |
| MLflow   | http://localhost:5001      |

### Données

```bash
python -m src.main --exchanges binance                    # OHLCV incrémental (binance)
python -m src.main --exchanges binance kraken             # Plusieurs exchanges
python -m src.main --schedule --exchanges binance         # Planifié quotidien (09:00)
python -m src.main --ticker --exchanges binance --runtime 120   # Ticker temps réel (120s)
python ops/scripts/collect_news.py --once                 # Collecte RSS (une passe)
python ops/scripts/fetch_history.py                       # Historique OHLCV complet
```

### Base de données

```bash
python -c "from src.api.dependencies import engine; print('DB :', engine.url)"   # Connexion active
python ops/scripts/check_db.py                            # Inspecte le contenu
python ops/scripts/migrate_to_postgres.py                 # Migre SQLite → PostgreSQL
```

### Tests

```bash
python -m pytest tests/ -v                                # Tous les tests
python -m pytest tests/test_api.py -v                     # Endpoints API
python -m pytest tests/test_paper_trading.py -v           # Paper trading
python -m pytest tests/ --cov=src --cov-report=term-missing   # Couverture de code
```

## Variables d'environnement

| Variable | Description |
|---|---|
| `POSTGRES_URL` | URL PostgreSQL (`postgresql://user:pwd@localhost/cryptodb`) |
| `ALERT_EMAIL_TO` | Destinataire des alertes de collecte |
| `ALERT_EMAIL_FROM` | Expéditeur SMTP |
| `ALERT_EMAIL_PASSWORD` | Mot de passe application Gmail |
| `ALERT_SMTP_HOST` | Serveur SMTP (défaut : `smtp.gmail.com`) |
| `ALERT_SMTP_PORT` | Port SMTP (défaut : `587`) |
| `MLFLOW_TRACKING_URI` | URI MLflow (défaut : `http://localhost:5001`) |

## API REST

L'API FastAPI expose les données OHLCV, les indicateurs de marché, les signaux techniques, les news et le paper trading. Elle démarre sur le port **8000** et génère automatiquement une documentation interactive.

→ [docs/api.md](docs/api.md)

## Frontend

Dashboard Streamlit en six pages : chandelier interactif, Market Overview (Fear & Greed, top movers, corrélations), signaux BUY/SELL/HOLD, veille actualités enrichie par NLP, backtesting ML et paper trading temps réel.

→ [docs/frontend.md](docs/frontend.md)

## Paper Trading

Simulation de stratégies sur capital fictif avec prix temps réel Binance (WebSocket `miniTicker`). Création de portefeuilles, ordres BUY/SELL, suivi des positions et P&L, métriques de performance (Sharpe, win rate, drawdown).

→ [docs/paper_trading_spec.md](docs/paper_trading_spec.md)

## Collecte de données

Pipeline ETL multi-exchange (ccxt) : OHLCV incrémental, ticker temps réel, historique complet et news RSS. Les articles sont enrichis automatiquement (sentiment VADER, mots-clés, entités, topics). Des alertes email sont envoyées aux abonnés à chaque collecte.

→ [docs/data_collection.md](docs/data_collection.md)

## ML, Backtesting & NLP

Évaluation de modèles (Random Forest, Régression Logistique, Dummy) sur fenêtres walk-forward avec purge et embargo. Métriques Sharpe, PnL, drawdown, comparaison buy-and-hold. Chaque expérience est tracée dans MLflow. Le module NLP enrichit les articles via TF-IDF, classification de topics et extraction d'entités.

→ [docs/ml.md](docs/ml.md)

## Structure du projet

```
├── src/                  # Tout le code applicatif
│   ├── api/              # API FastAPI (routers, schemas, dependencies, main.py, Dockerfile)
│   ├── frontend/         # UI Streamlit (pages, components, api_client, app.py, Dockerfile)
│   ├── collectors/       # OHLCV, ticker, news RSS, Fear & Greed, WebSocket
│   ├── collector/        # Dockerfile collecte planifiée
│   ├── etl/              # Pipeline Extract → Transform → Load
│   ├── models/           # Modèles SQLAlchemy
│   ├── paper_trading/    # Moteur paper trading (PaperTrader)
│   ├── services/         # LivePriceCache (WS), clients exchanges, contexts DB/exchange
│   ├── schedulers/       # Planificateurs OHLCV / ticker / market data
│   ├── analytics/        # Indicateurs techniques
│   ├── notifications/    # Alertes email
│   ├── ml/               # backtesting, feature_engineering, models, nlp
│   ├── quality/          # Validation des données (validator.py)
│   ├── config/           # settings.py, api_keys.py, config.yaml
│   ├── logger_settings.py
│   ├── metrics.py        # Métriques Prometheus
│   └── main.py           # Point d'entrée collecte OHLCV
├── ops/                  # Exploitation hors-app
│   ├── scripts/          # fetch_history.py, collect_news.py, migrate_to_postgres.py…
│   ├── notebooks/        # Notebooks d'analyse
│   ├── mlflow/           # Dockerfile + entrypoint MLflow
│   └── setup.sh          # Script d'installation multi-OS
├── docs/                 # Documentation technique (+ SAUVEGARDES.md)
├── tests/                # Suite de tests pytest
├── infra/                # Observabilité, Ansible, Nginx (déploiement VPS)
├── data/                 # Données (SQLite, raw/processed)
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

## Stack technique

| Couche | Technologie |
|---|---|
| Collecte | ccxt, CoinGecko API, feedparser |
| Prix temps réel | WebSocket Binance (`miniTicker`), `websockets` |
| Sentiment | vaderSentiment, Fear & Greed Index |
| NLP / Text Mining | scikit-learn TF-IDF, regex |
| Stockage | SQLAlchemy, SQLite (dev) / PostgreSQL (prod) |
| API | FastAPI, uvicorn |
| Frontend | Streamlit, Plotly, streamlit-autorefresh |
| ML | scikit-learn, XGBoost, pandas |
| Backtesting | Walk-forward maison (purge + embargo) |
| Suivi ML | MLflow |
| Alertes | SMTP / Gmail |
| Indicateurs | pandas-ta-classic |
| Infra | Docker, Docker Compose |
| Tests | pytest, pytest-cov, httpx |
