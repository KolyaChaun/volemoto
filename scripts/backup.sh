#!/bin/bash
# Создаёт pg_dump и сжимает в .gz
# Использование: ./scripts/backup.sh
# Результат: /tmp/volemoto_backup_2026-04-08_03-00.sql.gz

set -euo pipefail

# Загружаем .env если он есть
if [ -f "$(dirname "$0")/../.env" ]; then
  export $(grep -v '^#' "$(dirname "$0")/../.env" | xargs)
fi

DATE=$(date +"%Y-%m-%d_%H-%M")
BACKUP_FILE="/tmp/volemoto_backup_${DATE}.sql.gz"

echo "Starting backup: $BACKUP_FILE"

pg_dump "$DATABASE_URL" | gzip > "$BACKUP_FILE"

echo "Backup created: $BACKUP_FILE"
echo "$BACKUP_FILE"