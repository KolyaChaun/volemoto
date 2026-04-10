import logging

from celery import Task

from src.services.backup_service import BackupError, BackupService
from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="src.worker.tasks.backup.run_backup",
    max_retries=3,
    default_retry_delay=5 * 60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60 * 60,
    retry_jitter=True,
)
def run_backup(self: Task) -> str:
    logger.info(
        "Backup task started (attempt %d/%d)",
        self.request.retries + 1,
        self.max_retries + 1,
    )

    try:
        url = BackupService().run()
        logger.info("Backup task completed: %s", url)
        return url
    except BackupError as exc:
        logger.error("Backup misconfiguration: %s", exc)
        raise
    except Exception as exc:
        logger.warning(
            "Backup failed (attempt %d), will retry: %s",
            self.request.retries + 1,
            exc,
        )
        raise
