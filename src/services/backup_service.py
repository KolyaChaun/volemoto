import gzip
import logging
import os
import subprocess
from datetime import datetime

from src.core.config import settings
from src.services.storage import is_configured, storage

logger = logging.getLogger(__name__)


class BackupError(Exception):
    """помилка при створенні чи загрузці бекапа."""


class BackupService:
    TMP_DIR = "/tmp"

    def create_dump(self) -> str:
        date = datetime.now().strftime("%Y-%m-%d_%H-%M")
        out_path = os.path.join(self.TMP_DIR, f"volemoto_backup_{date}.sql.gz")

        logger.info("Running pg_dump → %s", out_path)
        proc = subprocess.Popen(
            ["pg_dump", str(settings.database_url)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert proc.stdout is not None
        with gzip.open(out_path, "wb") as gz_file:
            for chunk in iter(lambda: proc.stdout.read(65536), b""):  # type: ignore[union-attr]
                gz_file.write(chunk)
        _, stderr_data = proc.communicate()
        if proc.returncode != 0:
            raise BackupError(f"pg_dump failed: {(stderr_data or b'').decode()}")

        size_kb = os.path.getsize(out_path) // 1024
        logger.info("Dump created: %s (%d KB)", out_path, size_kb)
        return out_path

    @staticmethod
    def upload(file_path: str) -> str:
        filename = os.path.basename(file_path)
        key = f"backups/{filename}"
        logger.info("Uploading %s → R2:%s", file_path, key)
        url = storage.upload_from_path(file_path, key, content_type="application/gzip")
        logger.info("Uploaded: %s", url)
        return url

    @staticmethod
    def cleanup(file_path: str) -> None:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("Removed temp file: %s", file_path)

    def run(self) -> str:
        if not is_configured():
            raise BackupError(
                "R2 not configured. Set R2_ENDPOINT, R2_ACCESS_KEY, "
                "R2_SECRET_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL."
            )

        dump_path = self.create_dump()
        try:
            return self.upload(dump_path)
        finally:
            self.cleanup(dump_path)
