#!/bin/bash
# Spuštěí zálohování

set -euo pipefail

echo "==> Spouštím zálohování"
bash infrastructure/backups/backup_script.sh