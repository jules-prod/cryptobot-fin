# Crypto Bot

Plateforme de collecte, stockage et analyse de données crypto.
Pipeline ETL multi-exchange → base de données → API REST → dashboard Streamlit + veille actualités + backtesting ML + **paper trading temps réel** + suivi d'expériences MLflow.

Déployée en **production sur VPS** via un pipeline **CI/CD + Ansible** entièrement automatisé.
Des modes de déploiement **local** et **free cloud** sont également disponibles (voir [Autres modes de déploiement](#autres-modes-de-déploiement)).

## Déploiement (production) — VPS via CI/CD + Ansible

Tout push sur la branche `prod` déclenche le workflow GitHub Actions **« Deploy to VPS »** (`.github/workflows/deploy.yml`).

### Pipeline

1. **CI Gate** (`.github/workflows/ci.yml`) — **bloquant** :
   **Lint** (ruff) · **Tests** (pytest) · **Docker Build**
2. **Deploy via Ansible** (uniquement si le gate passe) :
   - Configure l'accès SSH au VPS, rend l'inventaire avec `VPS_HOST`
   - Joue `infra/ansible/playbooks/deploy.yml` : synchronise le dépôt, `docker compose build` + `up`, attend la disponibilité de l'API et du Frontend, smoke-test
   - Diagnostic post-déploiement + smoke-test externe sur le domaine

Déclenchement manuel possible : **Actions → Deploy to VPS → Run workflow** (`workflow_dispatch`).

### Cible

- **VPS Ubuntu**, domaine **dtsc-cryptobot.fr** servi par **Nginx** + **HTTPS Let's Encrypt**
- **12 services** orchestrés par `docker-compose.yml` :
  - Application : `api` (FastAPI), `collector`, `frontend` (Streamlit), `mlflow`
  - Observabilité : `grafana`, `prometheus`, `loki`, `tempo`, `otel-collector`, `promtail`, `node-exporter`, `nginx-exporter`
- **Grafana** (`/grafana/`) et **MLflow** (`/mlflow/`) protégés par authentification Nginx

### Playbooks Ansible — `infra/ansible/playbooks/`

| Playbook | Rôle |
|---|---|
| `provision.yml` | Prépare le VPS : Docker, Nginx, UFW, fail2ban, utilisateurs, durcissement SSH |
| `deploy.yml` | Déploie l'application : synchro du dépôt, `docker compose`, contrôles de santé |
| `ssl.yml` | Certificats HTTPS (Let's Encrypt / certbot) |
| `backup.yml` | Sauvegardes planifiées + métrique de fraîcheur exposée à Prometheus |

### Secrets — GitHub, environnement `production`

`VPS_HOST`, `VPS_SSH_KEY`, `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`, `SMTP_*`, clés API exchanges & marché.

## Autres modes de déploiement

Le déploiement de production reste le **VPS** (ci-dessus). Deux alternatives sont fournies :

### Local — `ops/local/`

Pour le développement et les démos. Tout est piloté par le **`Makefile`** (`make help`).

```bash
bash ops/setup.sh        # installation (multi-OS) + .venv + .env
make docker              # stack complète via docker compose
# ou sans Docker : make run  (API + Streamlit), make run-all (+ MLflow)
```

→ Détails dans [`ops/local/README.md`](ops/local/README.md)

### Free cloud (Render + Supabase) — `ops/free-cloud/`

Déploiement gratuit sur **Render.com** (API conteneurisée) + **Supabase** (PostgreSQL managé), mis en place par Mikaël. **Référence, non maintenue.**

→ Détails dans [`ops/free-cloud/README.md`](ops/free-cloud/README.md)

## Observabilité

- **Grafana** : dashboards **Business** (home, trading, ML) + **Technical** (API, collector, database, system, logs, traces)
- **Alerting** par email (dossiers Business + Technical)
- **Logs** centralisés (Loki / Promtail) · **traces** (Tempo / OpenTelemetry) · **métriques** (Prometheus)

→ Configuration dans `infra/`

## Configuration — variables d'environnement

| Variable | Description |
|---|---|
| `POSTGRES_URL` | URL PostgreSQL (`postgresql://user:pwd@host/cryptodb`) |
| `ALERT_EMAIL_TO` | Destinataire des alertes |
| `ALERT_EMAIL_FROM` | Expéditeur SMTP |
| `ALERT_EMAIL_PASSWORD` | Mot de passe application Gmail |
| `ALERT_SMTP_HOST` / `ALERT_SMTP_PORT` | Serveur SMTP (défaut : `smtp.gmail.com:587`) |
| `MLFLOW_TRACKING_URI` | URI du serveur MLflow |

## Fonctionnalités

| Domaine | Description | Doc |
|---|---|---|
| **API REST** | FastAPI : OHLCV, indicateurs de marché, signaux techniques, news, paper trading (port 8000, doc interactive) | [docs/api.md](docs/api.md) |
| **Frontend** | Streamlit : chandelier, Market Overview, signaux BUY/SELL/HOLD, news NLP, backtesting, paper trading | [docs/frontend.md](docs/frontend.md) |
| **Paper Trading** | Simulation sur capital fictif, prix temps réel Binance (WebSocket), P&L et métriques | [docs/paper_trading_spec.md](docs/paper_trading_spec.md) |
| **Collecte** | ETL multi-exchange (ccxt) : OHLCV, ticker, historique, news RSS enrichies (NLP) | [docs/data_collection.md](docs/data_collection.md) |
| **ML & NLP** | Backtesting walk-forward (purge/embargo), Sharpe/PnL/drawdown, tracé MLflow, TF-IDF | [docs/ml.md](docs/ml.md) |

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
│   ├── local/            # Déploiement local (doc) — piloté par le Makefile
│   ├── free-cloud/       # Déploiement Render + Supabase (Mikaël, référence)
│   ├── scripts/          # fetch_history.py, collect_news.py, migrate_to_postgres.py…
│   ├── notebooks/        # Notebooks d'analyse
│   ├── mlflow/           # Dockerfile + entrypoint MLflow
│   └── setup.sh          # Script d'installation multi-OS
├── docs/                 # Documentation technique (+ SAUVEGARDES.md)
├── tests/                # Suite de tests pytest
├── infra/                # Observabilité, Ansible, Nginx (déploiement VPS)
├── data/                 # Données (SQLite, raw/processed)
├── Makefile              # Point d'entrée des commandes locales
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

## Stack technique

| Couche | Technologie |
|---|---|
| Collecte | ccxt, CoinGecko API, feedparser |
| Prix temps réel | WebSocket Binance (`miniTicker`), `websockets` |
| Sentiment / NLP | vaderSentiment, Fear & Greed Index, scikit-learn TF-IDF |
| Stockage | SQLAlchemy, PostgreSQL (prod) / SQLite (dev) |
| API | FastAPI, uvicorn |
| Frontend | Streamlit, Plotly |
| ML | scikit-learn, XGBoost, pandas |
| Suivi ML | MLflow |
| Infra | Docker, Docker Compose, Ansible, Nginx |
| CI/CD | GitHub Actions (CI Gate + Deploy via Ansible) |
| Observabilité | Grafana, Prometheus, Loki, Tempo, OpenTelemetry |
| Tests | pytest, pytest-cov, httpx |
```
