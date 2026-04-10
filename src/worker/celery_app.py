from celery import Celery
from celery.schedules import crontab

from src.core.config import settings

celery_app = Celery(
    "volemoto",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.worker.tasks.backup"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Kyiv",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    result_expires=60 * 60 * 24,
    beat_schedule={
        "daily-db-backup": {
            "task": "src.worker.tasks.backup.run_backup",
            "schedule": crontab(hour=3, minute=0, day_of_week=1),
            "options": {"expires": 60 * 60},
        },
    },
)
