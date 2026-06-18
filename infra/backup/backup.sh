#!/bin/bash
# CryptoBot canonical backup — runs as root from cron (0 3 * * *).
#
# Backs up the real data store (SQLite at data/crypto_data.db), the .env config,
# and Grafana state, then publishes a node-exporter textfile freshness metric
# consumed by the Grafana alert "alert-backup-stale"
# (time() - max(cryptobot_backup_last_success_timestamp_seconds) > 26h).
#
# Regression fixed (2026-06): the previous /opt/backups/backup.sh dumped a
# non-existent `cryptobot-timescaledb-1` postgres container — the stack runs on
# SQLite — so `set -euo pipefail` aborted on line 1 and the freshness metric was
# never refreshed, firing the backup-stale alert every eval cycle.

set -uo pipefail

COMPOSE_DIR="${CRYPTOBOT_DIR:-/home/ubuntu/cryptobot}"
BACKUP_DIR="${BACKUP_DIR:-/opt/backups}"
TEXTFILE_DIR="${TEXTFILE_DIR:-/var/lib/node_exporter/textfile}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
DATE="$(date +%Y%m%d_%H%M%S)"

mkdir -p "${BACKUP_DIR}"

log() { echo "[$(date '+%F %T')] $*"; }

data_ok=0

# 1. Real data store: SQLite data dir (authoritative — this is what must stay fresh).
if [ -d "${COMPOSE_DIR}/data" ]; then
  if tar czf "${BACKUP_DIR}/data_${DATE}.tar.gz" -C "${COMPOSE_DIR}" data/; then
    data_ok=1
    log "data dir backed up -> data_${DATE}.tar.gz"
  else
    log "ERROR: data dir tar failed"
  fi
else
  log "ERROR: data dir ${COMPOSE_DIR}/data not found"
fi

# 2. Config (.env) — best effort.
if [ -f "${COMPOSE_DIR}/.env" ]; then
  cp "${COMPOSE_DIR}/.env" "${BACKUP_DIR}/env_${DATE}.bak" && log "env backed up"
fi

# 3. Grafana state (dashboards/db) — best effort, never blocks the metric.
if docker exec cryptobot-grafana-1 tar czf "/tmp/grafana_${DATE}.tar.gz" /var/lib/grafana/ 2>/dev/null \
   && docker cp "cryptobot-grafana-1:/tmp/grafana_${DATE}.tar.gz" "${BACKUP_DIR}/" 2>/dev/null; then
  docker exec cryptobot-grafana-1 rm -f "/tmp/grafana_${DATE}.tar.gz" 2>/dev/null || true
  log "grafana state backed up"
else
  log "WARN: grafana backup skipped"
fi

# 4. Publish freshness metric — ONLY on a successful data backup, atomically.
if [ "${data_ok}" -eq 1 ]; then
  mkdir -p "${TEXTFILE_DIR}"
  TMP="${TEXTFILE_DIR}/.cryptobot_backup.prom.$$"
  {
    echo '# HELP cryptobot_backup_last_success_timestamp_seconds Unix time of the last successful backup.'
    echo '# TYPE cryptobot_backup_last_success_timestamp_seconds gauge'
    echo "cryptobot_backup_last_success_timestamp_seconds $(date +%s)"
  } > "${TMP}"
  mv "${TMP}" "${TEXTFILE_DIR}/cryptobot_backup.prom"
  log "freshness metric published"
fi

# 5. Retention.
find "${BACKUP_DIR}" -maxdepth 1 -name 'data_*.tar.gz'    -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null || true
find "${BACKUP_DIR}" -maxdepth 1 -name 'env_*.bak'        -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null || true
find "${BACKUP_DIR}" -maxdepth 1 -name 'grafana_*.tar.gz' -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null || true

if [ "${data_ok}" -eq 1 ]; then
  log "backup OK"
  exit 0
fi
log "backup FAILED (data dir not backed up; metric not refreshed)"
exit 1
