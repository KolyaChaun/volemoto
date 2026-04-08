#!/bin/bash
# Устанавливает ежедневный бэкап в cron
# Запуск: bash scripts/setup_cron.sh

CRON_JOB="0 3 * * * cd /root/volemoto && docker-compose exec -T db pg_dump -U volemoto volemoto | gzip > /tmp/backup_\$(date +\%Y-\%m-\%d).sql.gz && docker-compose exec -T app python scripts/backup_to_r2.py /tmp/backup_\$(date +\%Y-\%m-\%d).sql.gz >> /var/log/volemoto_backup.log 2>&1"

# Проверяем что такой job ещё не добавлен
if crontab -l 2>/dev/null | grep -q "backup_to_r2"; then
    echo "Cron job already exists, skipping."
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added. Backups will run daily at 03:00."
fi

echo "Current crontab:"
crontab -l