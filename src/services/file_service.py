import os, uuid, shutil
from typing import List
from fastapi import UploadFile

CATEGORY_FOLDER = {"moto": "moto", "moped": "moped", "quad": "quad"}


def save_photos(files: List[UploadFile], category: str = "moto") -> List[str]:
    folder   = CATEGORY_FOLDER.get(category, "moto")
    dir_path = f"src/media/{folder}"
    os.makedirs(dir_path, exist_ok=True)
    paths = []
    for f in files:
        if f and f.filename:
            ext      = f.filename.rsplit(".", 1)[-1]
            filename = f"{uuid.uuid4().hex}.{ext}"
            with open(f"{dir_path}/{filename}", "wb") as out:
                shutil.copyfileobj(f.file, out)
            paths.append(f"/media/{folder}/{filename}")
    return paths


def save_single_file(upload: UploadFile, folder: str) -> str:
    if not upload or not upload.filename:
        return ""
    ext      = upload.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    dir_path = f"src/media/{folder}"
    os.makedirs(dir_path, exist_ok=True)
    with open(f"{dir_path}/{filename}", "wb") as out:
        shutil.copyfileobj(upload.file, out)
    return f"/media/{folder}/{filename}"
