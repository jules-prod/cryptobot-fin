# Crypto Bot

Plateforme de collecte, stockage et analyse de données crypto.  
Pipeline ETL multi-exchange → base de données → API REST → dashboard Streamlit + veille actualités + backtesting ML + **paper trading temps réel** + suivi d'expériences MLflow.

## Installation

```bash
make setup
```

`ops/setup.sh` détecte l'OS et installe les dépendances adaptées :

| OS | Support |
|---|---|
| macOS | Homebrew + libpq |
| Linux (Debian/Ubuntu) | apt — `python3-dev libpq-dev` |
| Linux (RedHat) | yum — `python3-devel postgresql-devel` |
| Linux (Arch / Alpine) | pacman / apk |
| Windows | Non supporté nativement — utiliser WSL2 ou `make docker` |

Le script vérifie Python 3.10+, crée un `.venv` si nécessaire, installe `requirements.txt` et copie `.env.example` → `.env`.  
Éditez `.env` avec vos clés API avant de lancer les collectes.

## Démarrage rapide

```bash
make setup      # Installation (première fois)

make run        # API (8000) + Streamlit (8501)
make run-all    # API + MLflow (5001) + Streamlit — tout en un
make docker     # Stack complète via Docker
make help       # Toutes les commandes disponibles
```

## Commandes make

### Local (sans Docker)

```bash
make run                    # API FastAPI + Streamlit (SQLite par défaut)
make run DB=postgres        # Idem avec PostgreSQL
make run-all                # API + MLflow + Streamlit en un seul processus
make stop                   # Arrête l'API (Ctrl+C arrête Streamlit)
make mlflow                 # Lance MLflow seul sur le port 5001
```

### Docker

```bash
make docker                 # Build et démarre tous les services
make docker-stop            # Arrête tous les conteneurs
make docker-logs            # Logs en temps réel
```

| Service  | URL                        |
|----------|----------------------------|
| API REST | http://localhost:8000/docs |
| Frontend | http://localhost:8501      |
| MLflow   | http://localhost:5001      |

### Données

```bash
make collect                               # OHLCV incrémental (binance)
make collect EXCHANGES="binance kraken"
make collect-schedule                      # Planifié quotidien
make ticker                                # Ticker temps réel (120s)
make collect-live                          # OHLCV + ticker en parallèle
make news                                  # Collecte RSS (une passe)
make history                               # Historique OHLCV complet
```

### Base de données

```bash
make db-check               # Vérifie la connexion active
make db-inspect             # Inspecte le contenu
make db-migrate             # Migre SQLite → PostgreSQL
```

### Tests

```bash
make tests        # Tous les tests
make test-api     # Endpoints API
make test-paper   # Paper trading
make test-cov     # Couverture de code
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
│   ├── etl/              # Pipeline Extract → Transform → Load
│   ├── models/           # Modèles SQLAlchemy
│   ├── paper_trading/    # Moteur paper trading (PaperTrader)
│   ├── services/         # LivePriceCache (singleton WS), clients exchanges
│   ├── analytics/        # Indicateurs techniques
│   ├── notifications/    # Alertes email
│   ├── ml/               # backtesting, feature_engineering, models, nlp
│   ├── config/           # settings.py (Config/YAML), api_keys.py, config.yaml
│   ├── collector/        # Dockerfile collecte planifiée
│   ├── logger_settings.py
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
├── Makefile
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
