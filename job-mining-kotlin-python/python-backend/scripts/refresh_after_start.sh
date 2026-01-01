#!/usr/bin/env bash
# Polls the python backend until /system/status is UP, then triggers /internal/admin/refresh-knowledge.
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:8000}
MAX_RETRIES=${MAX_RETRIES:-60}
SLEEP=${SLEEP:-2}

for i in $(seq 1 "$MAX_RETRIES"); do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/system/status" || true)
  if [ "$status" = "200" ]; then
    break
  fi
  sleep "$SLEEP"
done

curl -s -X POST "$BASE_URL/internal/admin/refresh-knowledge" -H "Content-Type: application/json" && echo "\nrefresh triggered"
