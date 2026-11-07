#!/bin/bash
# Spuštění vývojového prostředí

set -euo pipefail

echo "==> Kontrola .env"
if [ ! -f .env ]; then
    echo "Kopíruji .env.example -> .env"
    cp .env.example .env
fi

echo "==> Instalace Python závislostů"
pip install -e .

echo "==> Kontrola Ollama modelů"
ollama pull qwen2.5:3b || true
ollama pull qwen2.5:14b || true
ollama pull nomic-embed-text || true

echo "==> Spuštění backend API"
python -m src.api.main