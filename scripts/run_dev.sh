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

echo "==> Vygeneruji .env z jediného zdroje pravdy (configs/models.yaml)"
python3 -c "
import yaml
with open('configs/models.yaml', encoding='utf-8') as f:
    data = yaml.safe_load(f)
models = {m['role']: m['name'] for m in data['models'].values()}
with open('.env', 'w', encoding='utf-8') as f:
    f.write(f'MODEL_SMALL={models[\"small\"]}\n')
    f.write(f'MODEL_LARGE={models[\"large\"]}\n')
    f.write(f'MODEL_COMPLEX={models[\"complex\"]}\n')
    f.write(f'MODEL_EMBEDDING={models[\"embedding\"]}\n')
print('==> .env vygenerován')
"

echo "==> Kontrola Ollama modelů"
for model in qwen3.5:4b qwen3:14b hf.co/Qwen/Qwen3-14B-GGUF:Q5_K_M nomic-embed-text; do
    ollama pull "$model" || true
done

echo "==> Spuštění backend API"
python -m src.api.main