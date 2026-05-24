---
marp: true
theme: default
paginate: true
style: |
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

  * {
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    box-sizing: border-box;
  }

  section {
    background: #ffffff;
    color: #111111;
    padding: 56px 64px;
    font-size: 18px;
    line-height: 1.6;
  }

  h1 {
    font-size: 36px;
    font-weight: 700;
    color: #111111;
    margin-bottom: 8px;
    border-bottom: 2px solid #111111;
    padding-bottom: 12px;
  }

  h2 {
    font-size: 26px;
    font-weight: 600;
    color: #111111;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #111111;
    margin-bottom: 8px;
  }

  ul {
    padding-left: 20px;
    margin: 0;
  }

  li {
    margin-bottom: 8px;
  }

  strong {
    font-weight: 600;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 15px;
    margin-top: 12px;
  }

  th {
    background: #111111;
    color: #ffffff;
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
  }

  td {
    padding: 7px 12px;
    border-bottom: 1px solid #e0e0e0;
  }

  tr:last-child td {
    border-bottom: none;
  }

  code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 14px;
    font-family: 'IBM Plex Mono', 'Courier New', monospace;
  }

  pre {
    background: #f4f4f4;
    padding: 16px;
    border-radius: 4px;
    font-size: 13px;
    font-family: 'IBM Plex Mono', 'Courier New', monospace;
    line-height: 1.5;
  }

  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    margin-top: 16px;
  }

  .label {
    display: inline-block;
    background: #111111;
    color: #ffffff;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 2px 8px;
    border-radius: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
  }

  footer {
    font-size: 12px;
    color: #888888;
  }
---

<!-- Slide 1 — Titre -->

# Crypto Bot

**Plateforme d'aide à la décision sur les marchés crypto**

<br>

Jules Willard · Mikaël Jayet

Octobre 2025 – Juin 2026

---

<!-- Slide 2 — Contexte & Objectif -->

# Contexte & Objectif

**Sujet DataScientest** : *"Créer un bot de trading basé sur un modèle de ML qui investira sur les marchés crypto"*

Notre réponse : une **plateforme complète d'aide à la décision**

<br>

<div class="columns">
<div>

### 3 personas identifiés

- **Noah** — Trader indépendant : signaux actionnables, transparence ML
- **Sarah** — Journaliste financière : veille NLP, filtrage du bruit
- **Aleksandar** — Débutant : paper trading pédagogique

</div>
<div>

### Notre angle

Combiner dans un seul outil open-source :
**ETL + NLP + signaux + ML backtesting + paper trading**

</div>
</div>

---

<!-- Slide — User Journey -->

# Parcours utilisateur

<div style="margin-top:24px; display:flex; flex-direction:column; gap:22px; font-size:14px;">

<div style="display:flex; align-items:center; gap:14px;">
<div style="min-width:155px; padding:10px 12px; border-left:3px solid #111;">
<div style="font-weight:700; font-size:15px;">Noah</div>
<div style="font-size:12px; color:#666; margin-top:2px;">Trader indépendant</div>
</div>
<div style="display:flex; align-items:center; gap:8px; flex:1; flex-wrap:nowrap;">
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center;">Signaux<br>BUY/SELL/HOLD</div>
<span style="font-size:18px;">→</span>
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center;">Dashboard<br>chandelier</div>
<span style="font-size:18px;">→</span>
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center;">ML<br>Backtesting</div>
<span style="font-size:18px;">→</span>
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center; background:#111; color:#fff;">Paper<br>Trading</div>
</div>
</div>

<div style="display:flex; align-items:center; gap:14px;">
<div style="min-width:155px; padding:10px 12px; border-left:3px solid #111;">
<div style="font-weight:700; font-size:15px;">Sarah</div>
<div style="font-size:12px; color:#666; margin-top:2px;">Journaliste financière</div>
</div>
<div style="display:flex; align-items:center; gap:8px; flex:1; flex-wrap:nowrap;">
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center;">Veille NLP<br>actualités</div>
<span style="font-size:18px;">→</span>
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center;">Market<br>Overview</div>
<span style="font-size:18px;">→</span>
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center; background:#111; color:#fff;">Alertes<br>email</div>
</div>
</div>

<div style="display:flex; align-items:center; gap:14px;">
<div style="min-width:155px; padding:10px 12px; border-left:3px solid #111;">
<div style="font-weight:700; font-size:15px;">Aleksandar</div>
<div style="font-size:12px; color:#666; margin-top:2px;">Investisseur débutant</div>
</div>
<div style="display:flex; align-items:center; gap:8px; flex:1; flex-wrap:nowrap;">
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center;">Market<br>Overview</div>
<span style="font-size:18px;">→</span>
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center;">Signaux<br>expliqués</div>
<span style="font-size:18px;">→</span>
<div style="border:1.5px solid #111; padding:8px 12px; font-size:13px; text-align:center; background:#111; color:#fff;">Paper<br>Trading</div>
</div>
</div>

</div>

---

<!-- Slide — Architecture globale (archi 1/2) -->

# Architecture globale

```
 Sources de données
 Binance · Kraken · Coinbase · CoinGecko · RSS · WebSocket
        │ ccxt / feedparser / websockets
        ▼
 Pipeline ETL      Extract → Validate → Transform → Load
        │ SQLAlchemy ORM
        ▼
 Base de données   SQLite (dev) / PostgreSQL (prod & cloud Supabase)
        │                                │
        ▼                                ▼
 API FastAPI                      ML Pipeline
 30+ endpoints                    Walk-forward · XGBoost · MLflow
        │ HTTP / WebSocket
        ▼
 Frontend Streamlit — 6 pages
```

<br>

| Couche | Stack |
|---|---|
| Collecte | ccxt, feedparser, websockets |
| Stockage | SQLAlchemy · PostgreSQL · Supabase |
| API | FastAPI · Pydantic v2 · uvicorn |
| Frontend | Streamlit · Plotly |
| ML | scikit-learn · XGBoost · MLflow · DagsHub |

---

<!-- Slide 4 — Infrastructure & déploiement (archi 2/2) -->

# Infrastructure & déploiement

<div class="columns">
<div>

### Stack VPS (`_v1/infra/`)

- **Docker Compose** — API + Frontend + MLflow
- **Ansible** — provision VPS, sauvegardes, SSL
- **Nginx** — reverse proxy, rate limiting, WebSocket
- **Prometheus + Grafana** — 4 dashboards (API, business, PostgreSQL, système)
- **GitHub Actions** — CI/CD sur chaque PR (branches `main` et `dev` protégées)

</div>
<div>

### Cloud POC (free tier)

- **Render** — API FastAPI déployée en continu
- **Supabase** — PostgreSQL managé
- **Streamlit Cloud** — frontend déployé
  `https://nubxasqsgjdunghlifcfzn.streamlit.app/`
- **DagsHub** — MLflow tracking distant
- **GitHub Actions** — collecte quotidienne + alertes email matin (Kraken par défaut)

</div>
</div>

<br>

> 22 diagrammes UML versionnés (`docs/diagrams/`) · `setup.sh` multi-OS · Dev Container · 88 Pull Requests

---

<!-- Slide — Data Pipeline & ETL -->

# Data Pipeline & ETL

<div style="margin-top:10px; display:grid; grid-template-rows:1fr 1fr 1fr; height:530px; gap:8px;">

<!-- BANDE 1 -->
<div style="background:#f9f9f9; border:1px solid #ddd; border-top:2px solid #111; display:flex; flex-direction:column; justify-content:center; padding:0 14px;">
<div style="font-weight:700; font-size:10px; letter-spacing:.1em; text-transform:uppercase; margin-bottom:8px;">Collecte <span style="font-weight:400; color:#777;">(main.py · GitHub Actions quotidien)</span></div>
<div style="display:flex; align-items:center; gap:0; font-size:12px;">
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">① Email start</div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1.5px solid #111; background:#fff; padding:8px 12px; font-weight:600; white-space:nowrap;">② OHLCVScheduler — ETL</div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">③ TickerScheduler (WebSocket)</div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">④ MarketData (CoinGecko)</div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">⑤ check_db</div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">⑥ Email end</div>
</div>
</div>

<!-- BANDE 2 : Zoom ETL -->
<div style="border:1px solid #ddd; border-top:2px solid #111; display:flex; flex-direction:column; padding:10px 14px;">
<div style="font-weight:700; font-size:10px; letter-spacing:.1em; text-transform:uppercase; margin-bottom:6px;">Zoom — OHLCVScheduler : pipeline ETL</div>
<div style="display:flex; align-items:stretch; flex:1; gap:0;">

<div style="flex:1; border:1px solid #ddd; padding:8px 10px;">
<div style="font-weight:700; font-size:10px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:5px; padding-bottom:4px; border-bottom:1px solid #eee;">Extract</div>
<div style="font-size:11px; color:#333; line-height:1.55;"><code>ccxt.fetch_ohlcv()</code><br>symbol · timeframe<br>limit = 1 000 bougies<br>retry ×3 (exp. backoff)</div>
</div>
<div style="display:flex; align-items:center; padding:0 5px; font-size:17px; color:#bbb;">→</div>

<div style="flex:1; border:1px solid #ddd; padding:8px 10px; background:#f9f9f9;">
<div style="font-weight:700; font-size:10px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:5px; padding-bottom:4px; border-bottom:1px solid #eee;">Validate</div>
<div style="font-size:11px; color:#333; line-height:1.55;"><code>DataValidator</code><br>high ≥ low<br>volumes &gt; 0<br>timestamps cohérents</div>
</div>
<div style="display:flex; align-items:center; padding:0 5px; font-size:17px; color:#bbb;">→</div>

<div style="flex:1.4; border:1px solid #ddd; padding:8px 10px;">
<div style="font-weight:700; font-size:10px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:5px; padding-bottom:4px; border-bottom:1px solid #eee;">Transform</div>
<div style="font-size:11px; color:#333; line-height:1.55;"><code>_to_dataframe()</code> List → df<br><code>_add_metadata()</code> exchange/symbol<br><code>_convert_timestamps()</code> ms → UTC<br><code>_enrich_data()</code> price_range, price_change_pct<br><code>_normalize_data()</code> cast · sort</div>
</div>
<div style="display:flex; align-items:center; padding:0 5px; font-size:17px; color:#bbb;">→</div>

<div style="flex:1.2; border:1px solid #ddd; padding:8px 10px; background:#f9f9f9;">
<div style="font-weight:700; font-size:10px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:5px; padding-bottom:4px; border-bottom:1px solid #eee;">Load</div>
<div style="font-size:11px; color:#333; line-height:1.55;"><code>_add_timestamps()</code><br><code>df.to_sql()</code> via<br><code>database_transaction()</code><br>batch_insert (≥ 1 000 lignes)<br>IntegrityError → doublons ignorés</div>
</div>
<div style="display:flex; align-items:center; padding:0 5px; font-size:17px; color:#bbb;">→</div>

<div style="flex:0.9; border:1.5px solid #111; padding:8px 10px; display:flex; flex-direction:column; justify-content:center; text-align:center;">
<div style="font-weight:700; font-size:10px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:5px;">PostgreSQL</div>
<div style="font-size:11px; color:#555;">OHLCV · Tickers<br>Market data · News</div>
</div>

</div>
</div>

<!-- BANDE 3 : Phase 2 -->
<div style="background:#f9f9f9; border:1px solid #ddd; border-top:2px solid #111; display:flex; flex-direction:column; justify-content:center; padding:0 14px;">
<div style="font-weight:700; font-size:10px; letter-spacing:.1em; text-transform:uppercase; margin-bottom:8px;">Analyse <span style="font-weight:400; color:#777;">(API FastAPI, à la demande)</span></div>
<div style="display:flex; align-items:center; gap:0; font-size:12px;">
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">TechnicalCalculator<br><span style="font-size:10px; color:#666;">RSI · MACD · BB · SMA · EMA</span></div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">signal_scorer<br><span style="font-size:10px; color:#666;">BUY / SELL / HOLD [-1, +1]</span></div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">FeatureBuilder<br><span style="font-size:10px; color:#666;">features ML</span></div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">Walk-forward · XGBoost/RF/LR</div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1px solid #ccc; background:#fff; padding:8px 12px; white-space:nowrap;">MLflow (DagsHub)</div>
<div style="color:#bbb; padding:0 6px; font-size:17px;">→</div>
<div style="border:1.5px solid #111; background:#fff; padding:8px 12px; font-weight:600; white-space:nowrap;">Streamlit — 6 pages</div>
</div>
</div>

</div>

---

<!-- Slide — Pipeline de données & NLP -->

# Pipeline de données

### Collecte multi-sources

| Source | Données | Mode |
|---|---|---|
| Binance / Kraken / Coinbase | OHLCV bougies | Incrémental quotidien, 1000 bougies |
| Binance WebSocket | Prix live | Continu (daemon thread) |
| CoinGecko | Fear & Greed, market cap, top movers | À la demande |
| RSS multi-sources | Actualités crypto | Boucle 60 min |

### ETL

`Extractor` → `DataValidator` → `Transformer` → `Loader`
Upsert par clé composite (exchange / symbol / timeframe / timestamp)

### NLP sur les actualités

- **VADER** — score de sentiment continu (−1 → +1)
- **TF-IDF** — extraction de mots-clés (unigrammes + bigrammes)
- **Entités** — symboles crypto, exchanges (regex + dictionnaire)
- **Topics** — 8 catégories : `regulation`, `hack_security`, `adoption`, `defi`, `nft`, `macro`, `price_action`, `general`

---

<!-- Slide 6 — Machine Learning & Backtesting -->

# Machine Learning & Backtesting

### Walk-forward anti-data-leakage

Fenêtre entraînement (60 j) → purge + embargo → fenêtre test (15 j)
Chaque fold évalué indépendamment. Résultats loggés automatiquement dans **MLflow (DagsHub)**.

### Modèles évalués

| Modèle | Rôle |
|---|---|
| Dummy Classifier | Baseline plancher |
| Régression Logistique | Baseline interprétable |
| Random Forest | Robustesse (ensemble bagging) |
| **XGBoost** | Modèle principal (gradient boosting) |

### Features automatiques (`FeatureBuilder`)

SMA 7/14/21/50 · EMA 7/14/21 · RSI 14 · MACD · Bollinger Bands · Volume relatif · Log-returns J+1/3/5 · Label directionnel J+1

### Métriques de performance

Sharpe annualisé · Win rate · PnL (log-returns) · Max drawdown · Profit factor · vs buy-and-hold

---

<!-- Slide 7 — Fonctionnalités utilisateur -->

# Fonctionnalités

### Dashboard Streamlit — 6 pages

| Page | Persona | Contenu |
|---|---|---|
| Dashboard | Noah | Chandelier Plotly · SMA / EMA / BB superposables |
| Market Overview | Sarah, Aleksandar | Fear & Greed · market cap · top movers · corrélations |
| Signaux | Noah | Score BUY / SELL / HOLD par actif (RSI · MACD · BB · SMA) |
| Veille | Sarah | News RSS enrichies NLP · filtres · abonnement alertes email |
| ML & Backtesting | Noah, DS | Walk-forward · Sharpe · PnL · drawdown · vs buy-and-hold |
| Paper Trading | Aleksandar | Portefeuilles fictifs · ordres live WebSocket · courbe capital |

<br>

**API REST FastAPI** — 30+ endpoints, 7 routeurs (`ohlcv`, `market`, `signals`, `news`, `ml`, `alerts`, `paper_trading`)

**Alertes email** (SMTP Gmail) — démarrage ETL, nouvelles actualités, erreurs critiques

---

<!-- Slide 8 — Bilan & Perspectives -->

# Bilan & Perspectives

### Ce que nous avons livré

| | |
|---|---|
| **88 Pull Requests · ~100 commits · 7 mois** | CI/CD depuis le premier commit |
| **9 / 10 sprints livrés** | Seul le RL n'a pas été implémenté |
| **20 fichiers de tests · ~450 fonctions** | pytest + couverture CI automatique |
| **Déploiement cloud opérationnel** | Render · Supabase · DagsHub |


### Perspectives

- **Reinforcement learning** — agent BUY/SELL/HOLD (Monte Carlo / Q-learning)
- **Données on-chain** — Glassnode, Dune Analytics (personas Noah)
- **Authentification JWT** — gestion multi-utilisateurs
- **Mise en prod VPS** — activation SSL, stack Prometheus/Grafana sur VPS
