#!/usr/bin/env bash
set -euo pipefail

START_TIME=$(date +%Y-%m-%dT%H:%M:%S%z)
echo "[$START_TIME] Starting Astrologer API container"

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}
API_BASE_PATH=${API_BASE_PATH:-/api}
LOG_LEVEL=${LOG_LEVEL:-info}
LOWER_LOG_LEVEL=$(printf "%s" "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')

echo "[INFO] Host: $HOST | Port: $PORT | Workers: $WORKERS | Base path: $API_BASE_PATH"

# Basic dependency check before booting the server
if ! python -c "import kerykeion" >/dev/null 2>&1; then
  echo "[ERROR] Kerykeion library not found."
  exit 1
fi

echo "[INFO] Dependencies validated. Starting Uvicorn..."

exec uvicorn app.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --workers "$WORKERS" \
  --proxy-headers \
  --forwarded-allow-ips='*' \
  --log-level "$LOWER_LOG_LEVEL"
