# Écarts — Diagrammes externes (3 PNG) vs Production réelle

**Date** : 2026-06-13
**Branche** : `agent/soutenance`
**Sources de vérité prod** :
- `docker compose ps` live sur VPS `54.37.38.118` (`/home/ubuntu/cryptobot`)
- Branche `prod` : `docker-compose.yml`, `infra/{nginx,prometheus,otel,loki,tempo,promtail,grafana,ansible}`
- nginx déployé : `/etc/nginx/sites-enabled/cryptobot.conf` (template `infra/ansible/templates/nginx-vhost.conf.j2`)

**Diagrammes externes audités** (faits par un contributeur externe, `data/01.png`, `02.png`, `03.png`) :
- `01.png` — vue déploiement « free tier » (Render / Supabase / Streamlit Cloud / DagsHub / GitHub Actions)
- `02.png` — pipeline ETL logique (collecte → transform → PostgreSQL Supabase)
- `03.png` — composants ML & signaux (logique)

**Diagrammes prod produits** (PlantUML, `docs/diagrams/parts/`) :
- `DP02-prod-deployment.puml` — déploiement VPS réel (12 conteneurs)
- `DP03-observability-pipeline.puml` — observabilité OTel/Prom/Loki/Tempo/Grafana
- `DP04-network-security.puml` — nginx reverse-proxy, TLS, auth_basic, rate-limit, UFW/fail2ban

---

## 1. Écart structurel majeur : hébergement free-tier ❌ vs VPS auto-hébergé ✅

`01.png` décrit une topologie **SaaS gratuite** qui ne correspond PAS à la prod actuelle.

| Élément `01.png` (externe) | Réalité prod | Verdict |
|---|---|---|
| **Render (api — free tier)** héberge WSPriceCollector + FastAPI + Notifier | API + collector = conteneurs Docker sur **VPS OVH** | ❌ Faux hébergeur |
| **Supabase** PostgreSQL 12 tables | **SQLite** `data/processed/crypto_data.db` (bind mount) | ❌ Mauvais SGBD |
| **Streamlit Community Cloud** (frontend) | Conteneur `frontend` Streamlit derrière nginx (`:8501`) | ❌ Faux hébergeur |
| **DagsHub** (MLflow tracking) | **MLflow auto-hébergé** (conteneur `mlflow`, backend SQLite, `127.0.0.1:5001`) | ❌ Faux hébergeur |
| **GitHub Actions** = runtime collecte (cron 08:00) | `collector` = conteneur daemon sur le VPS (cron interne 08:00) | ❌ Mauvais runtime |
| Notifier SMTP Gmail dans Render | Alerting **Grafana → SMTP Gmail** (pas un service applicatif dédié) | ⚠ Déplacé |

> **Conclusion** : `01.png` documente vraisemblablement un **plan d'hébergement initial / abandonné** (free tier). La prod est un **stack Docker Compose mono-VPS** avec reverse-proxy nginx et TLS.

---

## 2. Composants prod absents des 3 PNG

Toute la **couche observabilité** (7 conteneurs) est absente des diagrammes externes :

| Conteneur prod | Image | Rôle | Présent PNG ? |
|---|---|---|---|
| `prometheus` | prom/prometheus:v2.55.0 | métriques, TSDB 15j | ❌ |
| `loki` | grafana/loki:3.2.0 | logs, rétention 168h | ❌ |
| `tempo` | grafana/tempo:2.6.1 | traces distribuées | ❌ |
| `otel-collector` | otel-collector-contrib:0.111.0 | hub OTLP (traces/logs/metrics) | ❌ |
| `promtail` | grafana/promtail:3.2.0 | docker logs → Loki | ❌ |
| `grafana` | infra/grafana (v11) | dashboards + alerting | ❌ |
| `node-exporter` | prom/node-exporter:v1.8.2 | métriques hôte | ❌ |
| `nginx-exporter` | nginx-prometheus-exporter:1.4 | métriques nginx | ❌ |

Également absents :
- **nginx reverse-proxy host** (TLS Let's Encrypt, routage `/api` `/grafana` `/_stcore/`, en-têtes durcis)
- **Domaine `dtsc-cryptobot.fr`** (+ alias www) et **certificat SSL**
- **Durcissement** : UFW (22/80/443), fail2ban, rate-limiting nginx, backup cron 03:00
- **Réseau `crypto-net`** (bridge) reliant les conteneurs
- **Proxy sortant `/x/ → api.anthropic.com`**

---

## 3. Dérives prod détectées (à corriger côté infra, hors périmètre diagrammes)

Constats issus du diff live ↔ branche `prod` :

1. **`node-exporter` orphelin** : le conteneur tourne sur le VPS mais
   - n'est **pas** dans `docker-compose.yml` (branche `prod`) ;
   - n'est **pas** dans `infra/prometheus/prometheus.yml` (`scrape_configs`).
   → Métriques hôte non collectées malgré le conteneur actif. **Retiré des diagrammes** (DP02/DP03) car non exploité ; à supprimer du VPS ou à brancher dans Prometheus.
2. **Notifier SMTP applicatif** : aucun service `notifier` indépendant en prod ; l'envoi d'e-mails passe par **Grafana SMTP** (alerting). `01.png` montre un « Notifier SMTP Gmail » côté Render → inexact.

> **Correctif** : contrairement à une note antérieure, **MLflow EST exposé publiquement** via la route nginx `/mlflow/` (auth_basic `.htpasswd-mlflow`, `proxy_pass 127.0.0.1:5001`, `--static-prefix /mlflow`). Cf. DP04. Idem `/grafana/` (auth_basic). Les proxies `/x/` et `/y/` (api.anthropic.com) sont hors périmètre applicatif et **non représentés**.

---

## 4. Ce que les PNG capturent correctement (logique métier)

`02.png` (ETL) et `03.png` (ML) restent **valables au niveau logique** — ils décrivent le pipeline applicatif, pas le déploiement :

- `02.png` : collecte (Binance WS, Kraken/Coinbase REST, CoinGecko, Alternative.me, RSS) → transformers (ETL OHLCV, MarketData, NLP VADER/TF-IDF) → stockage. ✅ cohérent **sauf le SGBD cible** (PostgreSQL/Supabase affiché → en réalité SQLite ; cf. catalogue `ER01`).
- `03.png` : Rule Engine + Feature Engineering (43 features) + modèles (XGBoost/Dummy/LogReg/RandomForest) + Walk-Forward backtesting + MLflow → ✅ cohérent au niveau composants ; le « DagsHub MLflow Tracking » est à remplacer par **MLflow auto-hébergé**.

> Ces deux vues n'ont pas à être refaites pour le déploiement : elles sont déjà couvertes par le catalogue V2 (`C02-etl-components`, `C03-ml-components`, `C06-ml-backtesting-pipeline`). Seules les mentions **Supabase/PostgreSQL** et **DagsHub** sont à corriger si réutilisées en soutenance.

---

## 5. Synthèse pour la soutenance

| Question jury probable | Réponse appuyée sur la prod réelle |
|---|---|
| « Où est hébergé le bot ? » | VPS OVH unique, Docker Compose (12 conteneurs), nginx + TLS, domaine `dtsc-cryptobot.fr`. Pas de SaaS free-tier. |
| « Quelle base de données ? » | SQLite (fichier, bind mount `./data`) — choix KISS pour le volume actuel ; PostgreSQL envisagé en V3. |
| « Observabilité / monitoring ? » | Stack Grafana complète : Prometheus (métriques), Loki (logs), Tempo (traces) via OpenTelemetry Collector ; alerting e-mail. |
| « Sécurité ? » | TLS Let's Encrypt, reverse-proxy nginx, auth_basic sur `/grafana`, rate-limiting, UFW + fail2ban. |
| « Suivi des modèles ? » | MLflow auto-hébergé (pas DagsHub), backend SQLite, artifacts en volume Docker. |

**Action recommandée** : présenter `DP02/DP03/DP04` (prod réelle) et **ne pas** projeter `01.png` (topologie free-tier obsolète). `02.png`/`03.png` réutilisables avec correction SGBD + MLflow.
