#!/bin/bash
# Spustí Ollama server a stáhne konfigurované modely před předáním řízení hlavnímu procesu.

set -euo pipefail

MODELS="${OLLAMA_MODELS:-$(python3 -c "import yaml; print(','.join(m['name'] for m in yaml.safe_load(open('configs/models.yaml'))['models'].values()))")}"

echo "==> Spouštím Ollama server na pozadí..."
ollama serve &
OLLAMA_PID=$!

# Počkej na readiness Ollama API
echo "==> Čekám na Ollama API..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama API je připraveno."
        break
    fi
    sleep 2
done

# Stáhnout modely
IFS=',' read -ra MODEL_ARRAY <<< "$MODELS"
for model in "${MODEL_ARRAY[@]}"; do
    model=$(echo "$model" | xargs) # trim whitespace
    if [ -n "$model" ]; then
        echo "==> Stahuji model: $model"
        ollama pull "$model" || echo "Varování: nepodařilo se stáhnout $model"
    fi
done

echo "==> Všechny modely připraveny. Předávám řízení hlavnímu procesu Ollama."
wait "$OLLAMA_PID"