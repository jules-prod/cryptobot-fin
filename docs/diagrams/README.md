# CryptoBot — Diagrams V2

Ce dossier contient le catalogue UML V2 de CryptoBot, aligné sur l'état réel de la branche `main`.

## Contenu

| Fichier | Description |
|---------|-------------|
| `_all-diagrams.md` | Catalogue principal — 22 diagrammes PlantUML intégrés |
| `parts/` | Fragments sources `.puml` (un fichier par diagramme) |
| `_v1/` | Catalogue V1 archivé (features fantômes — ne pas modifier) |

## Table de correspondance V1 → V2 (22 diagrammes)

| ID | Slug V2 | Titre V2 | Pivot V2 ? | Titre V1 (si différent) |
|----|---------|----------|------------|------------------------|
| AC01 | etl-pipeline | Pipeline ETL V2 | | Pipeline ETL |
| AC02 | signal-lifecycle | Cycle de vie Signal V2 | | Cycle de vie Signal |
| C01 | macro-architecture | Architecture Macro V2 | | Architecture Macro |
| C02 | etl-components | Composants ETL V2 | | Composants ETL |
| C03 | ml-components | Composants ML V2 | | Composants ML |
| C04 | api-components | Composants API FastAPI V2 | | Composants API |
| C05 | frontend-components | Composants Frontend V2 | | Composants Frontend |
| C06 | ml-backtesting-pipeline | Pipeline ML Backtesting V2 | | Pipeline ML Backtesting |
| **C07** | **backlog-v3** | **Backlog V3** | **OUI** | Phase 2 Roadmap |
| CL01 | pydantic-models | Modèles Pydantic V2 | | Modèles Pydantic |
| CL02 | orm-models | Modèles ORM SQLAlchemy V2 | | Modèles ORM |
| CL03 | fastapi-schemas | Schemas FastAPI V2 | | Schemas FastAPI |
| CL04 | ml-evaluators | Evaluateurs ML V2 | | Evaluateurs ML |
| CL05 | exceptions | Hiérarchie Exceptions V2 | | Exceptions |
| DP01 | docker-compose | Déploiement Docker Compose V2 | | Déploiement Docker |
| ER01 | database-schema | Schema BDD SQLite V2 | | Schema BDD |
| **SQ01** | **health-and-alerts-flow** | **Healthcheck + Alerts Flow V2** | **OUI** | JWT Auth Flow |
| SQ02 | dashboard-data-flow | Dashboard Data Flow V2 | | Dashboard Data Flow |
| SQ03 | signal-generation-flow | Signal Generation Flow V2 | | Signal Generation Flow |
| **SQ04** | **paper-trading-order-flow** | **Paper Trading Order Flow V2** | **OUI** | Chatbot LLM Flow |
| ST01 | signal-state | Etat Signal V2 | | Signal State |
| UC01 | personas-usecases | Personas & Cas d'usage V2 | | Personas & Use Cases |

Les 3 pivots V2 (en gras) ont subi un changement sémantique majeur par rapport à V1 : SQ01, SQ04, C07.

## Rendu

### Plugin Obsidian PlantUML

Installer le plugin [PlantUML](https://github.com/joethei/obsidian-plantuml) dans Obsidian.
Ouvrir `_all-diagrams.md` — les blocs ` ```plantuml ` sont rendus automatiquement.

### CLI PlantUML

```bash
# Vérification syntaxe (tous les fragments)
plantuml -checkonly docs/diagrams/parts/*.puml

# Génération PNG
plantuml -tpng docs/diagrams/parts/AC01-etl-pipeline.puml

# Génération SVG (tous)
plantuml -tsvg docs/diagrams/parts/*.puml
```

## Diagrammes Production & Soutenance (hors catalogue V2)

Adaptation des 3 diagrammes externes (`data/0{1,2,3}.png`) à l'archi prod réelle (`docker compose ps` sur le VPS + branche `prod`), plus 2 vues complémentaires :

| ID | Adapté de | Fichier | Description |
|----|-----------|---------|-------------|
| DP02 | **01** | `parts/DP02-architecture-globale.puml` | Architecture globale — **vraie prod VPS** (nginx + Docker), SQLite, MLflow nginx, + sécurité & sauvegarde |
| DP05 | **02** | `parts/DP05-pipeline-etl.puml` | Pipeline ETL fidèle au 02 — Supabase PostgreSQL → **SQLite** |
| DP06 | **03** | `parts/DP06-composants-ml.puml` | Composants ML fidèles au 03 — SQLite + **MLflow nginx** (ex-DagsHub) |
| DP03 | — | `parts/DP03-observability-pipeline.puml` | Observabilité OTel → Prometheus/Loki/Tempo → Grafana + alerting |
| DP04 | — | `parts/DP04-network-security.puml` | nginx reverse-proxy, TLS, auth_basic, rate-limit, UFW/fail2ban |

> `DP01-docker-compose` reste la vue « code `main` » (4 services). DP02/DP05/DP06 = adaptation fidèle des 3 PNG. DP03/DP04 = compléments observabilité & sécurité.

**Corrections appliquées** vs PNG externes : `Supabase PostgreSQL → SQLite` (DP02/DP05/DP06) · `DagsHub MLflow Tracking → MLflow Deployment nginx` (DP02/DP06) · hébergement free-tier (Render/Streamlit Cloud) → **VPS réel** (DP02).

L'analyse détaillée des écarts est dans **`GAP-prod-vs-diagrammes-externes.md`**.

## Note sur `parts/`

Le dossier `parts/` contient les 22 fragments sources `.puml`. Chaque fichier :

- Commence par `@startuml {ID}-{slug}` (ligne 1)
- Intègre le bloc skin partagé `_common` (lignes 2–143/144)
- Se termine par `@enduml`

Ne pas modifier les fragments directement — ils constituent la source de vérité pour le catalogue.
