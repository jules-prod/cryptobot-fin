#!/usr/bin/env bash
# Entrypoint MLflow — lance le serveur sous le sous-chemin /mlflow.
#
# Auth : AUCUNE auth native MLflow. La protection est assurée UNIQUEMENT par
# nginx (auth_basic + /etc/nginx/.htpasswd-mlflow, identifiants Grafana, bcrypt).
# L'auth native (--app-name basic-auth) a été retirée : elle générait un
# basic_auth.ini lu par configparser, qui plante (502) dès que le mot de passe
# Grafana contient un caractère spécial (%, [, ], =, …).
set -euo pipefail

BACKEND_STORE_URI="sqlite:////mlflow/mlflow.db"

# Le backend store peut avoir été créé par une version MLflow DIFFÉRENTE.
# mlflow server REFUSE de démarrer si le schéma ne correspond pas (pas d'auto-downgrade).
#  1) migration idempotente (no-op si déjà à jour) ;
#  2) si le schéma vient d'une version plus récente (ex: 3.x → revision alembic inconnue
#     de la 2.x), 'mlflow db upgrade' échoue : on SAUVEGARDE la base puis on repart neuf
#     (les runs étaient des backtests de test). mv = réversible, jamais de perte silencieuse.
DB_FILE="/mlflow/mlflow.db"
echo "[mlflow-entrypoint] Migration schéma backend store (idempotent)…"
if ! mlflow db upgrade "${BACKEND_STORE_URI}"; then
  if [ -f "${DB_FILE}" ]; then
    BAK="${DB_FILE}.bak-$(date +%Y%m%d%H%M%S)"
    echo "[mlflow-entrypoint] WARN: schéma incompatible (probable downgrade 3.x→2.x). Sauvegarde ${DB_FILE} → ${BAK}, redémarrage sur base neuve." >&2
    mv "${DB_FILE}" "${BAK}"
    mlflow db upgrade "${BACKEND_STORE_URI}" || echo "[mlflow-entrypoint] WARN: init base neuve échouée — démarrage quand même." >&2
  else
    echo "[mlflow-entrypoint] WARN: 'mlflow db upgrade' a échoué (pas de fichier DB) — démarrage quand même." >&2
  fi
fi

# --static-prefix /mlflow : UI + API servies sous /mlflow (sous-chemin nginx).
# Pas de --app-name : auth déléguée à nginx (couche unique).
# Pas de --allowed-hosts : flag 3.x uniquement (absent en 2.x, ferait crasher le boot).
exec mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri "${BACKEND_STORE_URI}" \
  --default-artifact-root "/mlflow/artifacts" \
  --static-prefix /mlflow
