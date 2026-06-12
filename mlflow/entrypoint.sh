#!/usr/bin/env bash
# Entrypoint MLflow — génère la config basic-auth depuis l'environnement
# puis lance le serveur sous le sous-chemin /mlflow (cohérent avec Grafana).
#
# Aucun credential n'est stocké dans l'image : ils proviennent de
# MLFLOW_TRACKING_USERNAME / MLFLOW_TRACKING_PASSWORD (injectés via .env).
set -euo pipefail

MLFLOW_USER="${MLFLOW_TRACKING_USERNAME:-mlflow}"
MLFLOW_PASS="${MLFLOW_TRACKING_PASSWORD:-changeme}"
AUTH_CONFIG="/mlflow/basic_auth.ini"

# basic_auth.ini généré au runtime — jamais commité.
cat > "${AUTH_CONFIG}" <<EOF
[mlflow]
default_permission = READ
database_uri = sqlite:////mlflow/basic_auth.db
admin_username = ${MLFLOW_USER}
admin_password = ${MLFLOW_PASS}
authorization_function = mlflow.server.auth:authenticate_request_basic_auth
EOF
chmod 600 "${AUTH_CONFIG}"

export MLFLOW_AUTH_CONFIG_PATH="${AUTH_CONFIG}"

BACKEND_STORE_URI="sqlite:////mlflow/mlflow.db"

# Le backend store peut avoir été créé par une version MLflow antérieure.
# mlflow server REFUSE de démarrer si le schéma est périmé (pas d'auto-migration)
# → migration idempotente au boot. No-op si le schéma est déjà à jour.
echo "[mlflow-entrypoint] Migration schéma backend store (idempotent)…"
if ! mlflow db upgrade "${BACKEND_STORE_URI}"; then
  echo "[mlflow-entrypoint] WARN: 'mlflow db upgrade' a échoué — démarrage quand même." >&2
fi

# --app-name basic-auth   : auth native MLflow (2e couche, defense in depth)
# --static-prefix /mlflow : UI + API servies sous /mlflow (sous-chemin nginx)
exec mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri "${BACKEND_STORE_URI}" \
  --default-artifact-root "/mlflow/artifacts" \
  --static-prefix /mlflow \
  --app-name basic-auth \
  --allowed-hosts '*'
