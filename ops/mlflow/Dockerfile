FROM python:3.11-slim

# MLflow épinglé en 2.x : la 3.x sert une UI « auth-aware » qui appelle
# /ajax-api/2.0/mlflow/users/current (404 sans plugin auth) → page blanche derrière
# nginx. La 2.x rend l'UI directement. Pas d'extra [auth] : auth assurée par nginx.
RUN pip install --no-cache-dir "mlflow==2.18.0"

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /mlflow/artifacts

COPY ops/mlflow/entrypoint.sh /usr/local/bin/mlflow-entrypoint.sh
RUN chmod +x /usr/local/bin/mlflow-entrypoint.sh

EXPOSE 5000

# En MLflow 2.x, /health n'est PAS sous le static-prefix (contrairement à la 3.x) :
# l'endpoint vit à la racine /health (non authentifié), pas /mlflow/health.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/usr/local/bin/mlflow-entrypoint.sh"]
