#!/bin/bash
# Spuštění zálohování dat Causa (SQLite, ledger, vektory) dle nastavení v Settings/.env.
set -euo pipefail

echo "==> Spouštím zálohování dat Causa"
python -m src.core.backup