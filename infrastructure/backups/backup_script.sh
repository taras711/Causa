#!/bin/bash
# Skript pro šifrované zálohování databází a ledgeru

set -euo pipefail

SOURCE_DIR="/source"
TARGET_DIR="/target"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="causa_backup_${TIMESTAMP}.tar.gz"

mkdir -p "$TARGET_DIR"

tar -czf "/tmp/${BACKUP_FILE}" -C "$SOURCE_DIR" .

# Šifrování (pokud je k dispozici klíč)
if [ -n "${BACKUP_ENCRYPTION_KEY:-}" ]; then
    openssl enc -aes-256-cbc -salt -in "/tmp/${BACKUP_FILE}" \
        -out "${TARGET_DIR}/${BACKUP_FILE}.enc" \
        -pass env:BACKUP_ENCRYPTION_KEY
    rm -f "/tmp/${BACKUP_FILE}"
else
    mv "/tmp/${BACKUP_FILE}" "${TARGET_DIR}/${BACKUP_FILE}"
fi

echo "Záloha vytvořena: ${TARGET_DIR}/${BACKUP_FILE}"