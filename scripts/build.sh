#!/bin/bash
# Sestavení Docker obrazů

set -euo pipefail

echo "==> Sestavím Docker obrazy"
docker-compose -f infrastructure/docker-compose.yml build