#!/usr/bin/env bash
# Deploy crypto-bot stack via docker compose.
# Usage: bash scripts/deploy.sh
# Expects to run from the project root (/home/ubuntu/cryptobot on VPS).
set -euo pipefail

COMPOSE_FILE="docker-compose.yml"

echo "=== CryptoBot Deploy ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Dir:  $(pwd)"

# Sanity checks
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "ERROR: $COMPOSE_FILE not found in $(pwd)" >&2
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "ERROR: .env file missing — copy .env.example and fill values" >&2
  exit 1
fi

# Build and restart
echo "--- Building images ---"
docker compose build --parallel

echo "--- Stopping old containers ---"
docker compose down --remove-orphans --timeout 30

echo "--- Starting services ---"
docker compose up -d

echo "--- Waiting for healthchecks (max 90s) ---"
TIMEOUT=90
ELAPSED=0
while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
  HEALTHY=$(docker compose ps --format json 2>/dev/null | grep -c '"healthy"' || true)
  TOTAL=$(docker compose ps --format json 2>/dev/null | wc -l || true)
  echo "  ${HEALTHY}/${TOTAL} healthy (${ELAPSED}s)"

  if [ "$HEALTHY" -ge 2 ]; then
    # api + frontend healthy is enough
    break
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done

echo "--- Container status ---"
docker compose ps

# Final health verification
if curl -sf --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
  echo "API:      OK"
else
  echo "API:      FAIL" >&2
  docker compose logs api --tail 30
  exit 1
fi

if curl -sf --max-time 5 http://localhost:8501/_stcore/health > /dev/null 2>&1; then
  echo "Frontend: OK"
else
  echo "Frontend: FAIL" >&2
  docker compose logs frontend --tail 30
  exit 1
fi

echo "=== Deploy complete ==="
