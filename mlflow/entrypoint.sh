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

# Le backend store peut avoir été créé par une version MLflow antérieure.
# mlflow server REFUSE de démarrer si le schéma est périmé (pas d'auto-migration)
# → migration idempotente au boot. No-op si le schéma est déjà à jour.
echo "[mlflow-entrypoint] Migration schéma backend store (idempotent)…"
if ! mlflow db upgrade "${BACKEND_STORE_URI}"; then
  echo "[mlflow-entrypoint] WARN: 'mlflow db upgrade' a échoué — démarrage quand même." >&2
fi

# --static-prefix /mlflow : UI + API servies sous /mlflow (sous-chemin nginx).
# Pas de --app-name : auth déléguée à nginx (couche unique).
exec mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri "${BACKEND_STORE_URI}" \
  --default-artifact-root "/mlflow/artifacts" \
  --static-prefix /mlflow \
  --allowed-hosts '*'
