FROM python:3.11-slim

# mlflow[auth] tire les dépendances du plugin basic-auth (Flask, etc.)
RUN pip install --no-cache-dir "mlflow[auth]>=2.10.0"

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /mlflow/artifacts

COPY mlflow/entrypoint.sh /usr/local/bin/mlflow-entrypoint.sh
RUN chmod +x /usr/local/bin/mlflow-entrypoint.sh

EXPOSE 5000

# /health est servi sous le static-prefix et reste non authentifié.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:5000/mlflow/health || exit 1

ENTRYPOINT ["/usr/local/bin/mlflow-entrypoint.sh"]
