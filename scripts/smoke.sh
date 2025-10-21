#!/usr/bin/env bash

set -euo pipefail

printf '%s\n' 'Starting services...'
docker compose up -d --build

printf '%s\n' 'Waiting for backend healthcheck...'
until curl -fsS http://localhost/api/healthz >/dev/null 2>&1; do
  sleep 2
done

printf '%s\n' 'Backend is reachable.'
printf '%s\n' 'Open http://localhost to load the Telegram mini app shell.'

