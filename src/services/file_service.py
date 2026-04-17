import io
import os
import uuid
from typing import List

from fastapi import UploadFile
from PIL import Image
from pillow_heif import register_heif_opener

from src.services.storage import is_configured as r2_enabled
from src.services.storage import storage

register_heif_opener()


class InvalidFileError(Exception):
    """Raised when an uploaded file fails validation."""


CONTENT_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "gif": "image/gif",
}

HEIC_EXTENSIONS = {"heic", "heif"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _normalize_to_jpeg(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def save_photos(files: List[UploadFile], category: str = "moto") -> List[str]:
    return [save_single_file(f, category) for f in files if f and f.filename]


def save_single_file(upload: UploadFile, folder: str) -> str:
    if not upload or not upload.filename:
        return ""

    ext = upload.filename.rsplit(".", 1)[-1].lower()
    data = upload.file.read(MAX_FILE_SIZE + 1)
    if len(data) > MAX_FILE_SIZE:
        raise InvalidFileError(
            f"Файл перевищує максимальний розмір {MAX_FILE_SIZE // 1024 // 1024} МБ"
        )

    allowed = set(CONTENT_TYPES.keys()) | HEIC_EXTENSIONS
    if ext not in allowed:
        raise InvalidFileError(f"Недозволений тип файлу: .{ext}")

    if ext in HEIC_EXTENSIONS:
        data = _normalize_to_jpeg(data)
        ext = "jpeg"

    filename = f"{uuid.uuid4().hex}.{ext}"
    content_type = CONTENT_TYPES.get(ext, "image/jpeg")

    if r2_enabled():
        key = f"{folder}/{filename}"
        return storage.upload_file(io.BytesIO(data), key, content_type)

    dir_path = f"src/media/{folder}"
    os.makedirs(dir_path, exist_ok=True)
    with open(f"{dir_path}/{filename}", "wb") as out:
        out.write(data)
    return f"/media/{folder}/{filename}"


def delete_file_by_path(path: str) -> None:
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
