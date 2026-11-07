#!/bin/bash
# Nasazení na zákaznický server

set -euo pipefail

echo "==> Nasazuji produkční verzi"
docker-compose -f infrastructure/docker-compose.prod.yml up -d

echo "==> Spustím migrace databáze"
python scripts/migrate.py

echo "==> Hotovo. Ověřte http://localhost:8000/health"