import logging
from typing import IO

import boto3
from botocore.exceptions import ClientError

from src.core.config import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(
        settings.r2_endpoint
        and settings.r2_access_key
        and settings.r2_secret_key
        and settings.r2_bucket_name
        and settings.r2_public_url
    )


class StorageService:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.r2_endpoint,
                aws_access_key_id=settings.r2_access_key,
                aws_secret_access_key=settings.r2_secret_key,
                region_name="auto",
            )
        return self._client

    def upload_file(
        self, file_obj: IO[bytes], key: str, content_type: str = "image/jpeg"
    ) -> str:
        try:
            self.client.upload_fileobj(
                file_obj,
                settings.r2_bucket_name,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            return f"{settings.r2_public_url.rstrip('/')}/{key}"
        except ClientError as e:
            logger.error("R2 upload failed for key=%s: %s", key, e)
            raise

    def upload_from_path(
        self, file_path: str, key: str, content_type: str = "application/octet-stream"
    ) -> str:
        with open(file_path, "rb") as f:
            return self.upload_file(f, key, content_type)

    def delete_file(self, key: str) -> None:
        try:
            self.client.delete_object(Bucket=settings.r2_bucket_name, Key=key)
        except ClientError as e:
            logger.error("R2 delete failed for key=%s: %s", key, e)
            raise

    def key_from_url(self, url: str) -> str:
        return url.removeprefix(settings.r2_public_url.rstrip("/")).lstrip("/")


storage = StorageService()
