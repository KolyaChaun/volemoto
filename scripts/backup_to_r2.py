import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    async_mode = "--async" in sys.argv

    if async_mode:
        from src.worker.tasks.backup import run_backup

        result = run_backup.delay()
        logger.info("Backup task queued: task_id=%s", result.id)
    else:
        from src.services.backup_service import BackupService

        url = BackupService().run()
        logger.info("Backup complete: %s", url)


if __name__ == "__main__":
    main()
