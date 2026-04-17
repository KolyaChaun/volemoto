import random
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from src.services.file_service import delete_file_by_path, save_photos

T = TypeVar("T")


class BaseItemService(Generic[T]):
    _owner_id_attr: str

    def __init__(self, db: Session):
        self.repo = self._make_repo(db)

    def _make_repo(self, db: Session):
        raise NotImplementedError

    def _make_model(self, article: str, photo: str, data: dict) -> T:
        raise NotImplementedError

    def gen_article(self) -> str:
        while True:
            code = f"{random.randint(0, 999999):06d}"
            if not self.repo.article_exists(code):
                return code

    def create(self, data: dict, photo_files: list) -> T:
        photo_paths = save_photos(photo_files, data["category"])
        entity = self._make_model(
            article=self.gen_article(),
            photo=photo_paths[0] if photo_paths else "",
            data=data,
        )
        return self.repo.save(entity, photo_paths)

    def update(self, entity: T, data: dict, new_photo_files: list) -> T:
        new_paths = save_photos(new_photo_files, data.get("category", entity.category))
        self.repo.add_photos(entity.id, new_paths)
        for key, value in data.items():
            setattr(entity, key, value)
        self.repo.flush()
        all_paths = self.repo.photo_paths(entity.id)
        if not entity.photo or entity.photo not in all_paths:
            entity.photo = all_paths[0] if all_paths else ""
        self.repo.commit()
        return entity

    def delete(self, entity: T) -> None:
        for photo in entity.photos:
            delete_file_by_path(photo.path)
        self.repo.delete(entity)

    def set_main_photo(self, photo_id: int) -> int | None:
        photo = self.repo.get_photo(photo_id)
        if not photo:
            return None
        owner_id = getattr(photo, self._owner_id_attr)
        entity = self.repo.get(owner_id)
        entity.photo = photo.path
        self.repo.commit()
        return owner_id

    def delete_photo(self, photo_id: int) -> int | None:
        photo = self.repo.get_photo(photo_id)
        if not photo:
            return None
        owner_id = getattr(photo, self._owner_id_attr)
        delete_file_by_path(photo.path)
        self.repo.delete_photo(photo)
        self.repo.flush()
        entity = self.repo.get(owner_id)
        all_paths = self.repo.photo_paths(owner_id)
        if not entity.photo or entity.photo not in all_paths:
            entity.photo = all_paths[0] if all_paths else ""
        self.repo.commit()
        return owner_id
