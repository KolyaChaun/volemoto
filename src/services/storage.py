"""
Сервис для работы с S3-compatible хранилищем (Cloudflare R2).

Если переменные окружения R2_* не заданы — сервис не активен,
файлы сохраняются локально (см. file_service.py).
"""
import os
import logging
from typing import IO
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

R2_ENDPOINT   = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET     = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "").rstrip("/")  # https://pub-xxx.r2.dev


def is_configured() -> bool:
    """True если все R2 переменные заданы."""
    return bool(R2_ENDPOINT and R2_ACCESS_KEY and R2_SECRET_KEY and R2_BUCKET and R2_PUBLIC_URL)


class StorageService:
    """
    Тонкая обёртка над boto3 для Cloudflare R2.
    Клиент создаётся лениво при первом обращении.
    """

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=R2_ENDPOINT,
                aws_access_key_id=R2_ACCESS_KEY,
                aws_secret_access_key=R2_SECRET_KEY,
                region_name="auto",
            )
        return self._client

    def upload_file(self, file_obj: IO[bytes], key: str, content_type: str = "image/jpeg") -> str:
        """
        Загружает file_obj в бакет под именем key.
        Возвращает публичный URL файла.
        """
        try:
            self.client.upload_fileobj(
                file_obj,
                R2_BUCKET,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            return f"{R2_PUBLIC_URL}/{key}"
        except ClientError as e:
            logger.error("R2 upload failed for key=%s: %s", key, e)
            raise

    def upload_from_path(self, file_path: str, key: str, content_type: str = "application/octet-stream") -> str:
        """Загружает файл с диска по пути file_path."""
        with open(file_path, "rb") as f:
            return self.upload_file(f, key, content_type)

    def delete_file(self, key: str) -> None:
        """Удаляет файл из бакета по ключу."""
        try:
            self.client.delete_object(Bucket=R2_BUCKET, Key=key)
        except ClientError as e:
            logger.error("R2 delete failed for key=%s: %s", key, e)
            raise

    def key_from_url(self, url: str) -> str:
        """Извлекает ключ из публичного URL. https://pub.r2.dev/moto/abc.jpg → moto/abc.jpg"""
        return url.removeprefix(R2_PUBLIC_URL).lstrip("/")


# Единственный экземпляр — используется во всём проекте
storage = StorageService()