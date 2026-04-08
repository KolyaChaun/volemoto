import os
import uuid
import shutil
from typing import List

from fastapi import UploadFile

from src.services.storage import storage, is_configured as r2_enabled

CONTENT_TYPES = {
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
    "png":  "image/png",
    "webp": "image/webp",
    "gif":  "image/gif",
}


def save_photos(files: List[UploadFile], category: str = "moto") -> List[str]:
    return [
        save_single_file(f, category)
        for f in files
        if f and f.filename
    ]


def save_single_file(upload: UploadFile, folder: str) -> str:
    """
    Сохраняет файл в R2 или локально.
    Возвращает путь/URL для сохранения в БД.
    """
    if not upload or not upload.filename:
        return ""

    ext      = upload.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    if r2_enabled():
        key          = f"{folder}/{filename}"
        content_type = CONTENT_TYPES.get(ext, "image/jpeg")
        return storage.upload_file(upload.file, key, content_type)

    # Локальное хранилище (разработка / нет R2)
    dir_path = f"src/media/{folder}"
    os.makedirs(dir_path, exist_ok=True)
    with open(f"{dir_path}/{filename}", "wb") as out:
        shutil.copyfileobj(upload.file, out)
    return f"/media/{folder}/{filename}"


def delete_file_by_path(path: str) -> None:
    """
    Удаляет файл где бы он ни хранился:
    - /media/... → удаляет с диска
    - https://... → удаляет из R2
    """
    if not path:
        return

    if path.startswith("/media/"):
        disk_path = "src" + path
        if os.path.exists(disk_path):
            os.remove(disk_path)

    elif path.startswith("http") and r2_enabled():
        key = storage.key_from_url(path)
        if key:
            storage.delete_file(key)