"""
Загружает свежий дамп PostgreSQL в Cloudflare R2.

Использование:
    poetry run python scripts/backup_to_r2.py

В Docker:
    docker compose exec app python scripts/backup_to_r2.py

Cron (ежедневно в 03:00):
    0 3 * * * cd /path/to/volemoto && bash scripts/backup.sh | tail -1 | xargs -I{} poetry run python scripts/backup_to_r2.py {}
"""
import sys
import os
import subprocess
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from src.services.storage import storage, is_configured

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def create_backup() -> str:
    """Запускает backup.sh и возвращает путь к созданному файлу."""
    script = os.path.join(os.path.dirname(__file__), "backup.sh")
    result = subprocess.run(["bash", script], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"backup.sh failed:\n{result.stderr}")
    # Последняя строка stdout — путь к файлу
    return result.stdout.strip().splitlines()[-1]


def upload_backup(file_path: str) -> str:
    """Загружает файл бэкапа в R2 в папку backups/."""
    filename = os.path.basename(file_path)
    key      = f"backups/{filename}"
    logger.info("Uploading %s → R2:%s", file_path, key)
    url = storage.upload_from_path(file_path, key, content_type="application/gzip")
    logger.info("Uploaded: %s", url)
    return url


def cleanup(file_path: str) -> None:
    """Удаляет временный файл после загрузки."""
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info("Removed temp file: %s", file_path)


def main():
    if not is_configured():
        logger.error("R2 is not configured. Set R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL.")
        sys.exit(1)

    # Путь к файлу можно передать аргументом или создать новый
    if len(sys.argv) > 1:
        backup_file = sys.argv[1]
        if not os.path.exists(backup_file):
            logger.error("File not found: %s", backup_file)
            sys.exit(1)
    else:
        logger.info("Creating backup...")
        backup_file = create_backup()

    try:
        upload_backup(backup_file)
    finally:
        cleanup(backup_file)

    logger.info("Backup complete.")


if __name__ == "__main__":
    main()