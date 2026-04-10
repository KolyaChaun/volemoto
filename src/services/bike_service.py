import random

from sqlalchemy.orm import Session

from src.models.bike import Bike
from src.repositories.bike_repo import BikeRepository
from src.services.file_service import delete_file_by_path, save_photos


class BikeService:
    def __init__(self, db: Session):
        self.repo = BikeRepository(db)

    def gen_article(self) -> str:
        while True:
            code = f"{random.randint(0, 999999):06d}"
            if not self.repo.article_exists(code):
                return code

    def create(self, data: dict, photo_files: list) -> Bike:
        photo_paths = save_photos(photo_files, data["category"])
        bike = Bike(
            article=self.gen_article(),
            photo=photo_paths[0] if photo_paths else "",
            **data,
        )
        return self.repo.save(bike, photo_paths)

    def update(self, bike: Bike, data: dict, new_photo_files: list) -> Bike:
        new_paths = save_photos(new_photo_files, data.get("category", bike.category))
        self.repo.add_photos(bike.id, new_paths)
        for key, value in data.items():
            setattr(bike, key, value)
        self.repo.flush()
        all_paths = self.repo.photo_paths(bike.id)
        if not bike.photo or bike.photo not in all_paths:
            bike.photo = all_paths[0] if all_paths else ""
        self.repo.commit()
        return bike

    def delete(self, bike: Bike) -> None:
        for photo in bike.photos:
            delete_file_by_path(photo.path)
        self.repo.delete(bike)

    def set_main_photo(self, photo_id: int) -> int | None:
        photo = self.repo.get_photo(photo_id)
        if not photo:
            return None
        bike = self.repo.get(photo.bike_id)
        bike.photo = photo.path
        self.repo.commit()
        return photo.bike_id

    def delete_photo(self, photo_id: int) -> int | None:
        photo = self.repo.get_photo(photo_id)
        if not photo:
            return None
        bike_id = photo.bike_id
        delete_file_by_path(photo.path)
        self.repo.delete_photo(photo)
        self.repo.flush()
        bike = self.repo.get(bike_id)
        all_paths = self.repo.photo_paths(bike_id)
        if not bike.photo or bike.photo not in all_paths:
            bike.photo = all_paths[0] if all_paths else ""
        self.repo.commit()
        return bike_id
