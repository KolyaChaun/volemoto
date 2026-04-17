import random
from typing import Optional

from sqlalchemy.orm import Session

from src.models.bike import Bike
from src.repositories.bike_repo import BikeFilters, BikeRepository
from src.services.currency_service import get_cached_rate
from src.services.file_service import delete_file_by_path, save_photos


def resolve_price_currency(raw: Optional[str]) -> tuple[str, float, bool]:
    currency = raw if raw in ("uah", "usd") else "usd"
    rate = get_cached_rate()
    rate_available = rate is not None and rate > 1
    if not rate_available:
        rate = 1.0
        currency = "usd"
    return currency, rate, rate_available


def build_bike_filters(
    *,
    sort: str,
    brand: Optional[str],
    min_price: Optional[str],
    max_price: Optional[str],
    min_year: Optional[str],
    max_year: Optional[str],
    condition: Optional[str],
    available_only: bool,
    min_mileage: Optional[str],
    max_mileage: Optional[str],
    min_engine: Optional[str],
    max_engine: Optional[str],
    price_currency: str,
    usd_rate: float,
) -> BikeFilters:
    def _int(v: Optional[str]) -> Optional[int]:
        return int(v) if v and v.strip() else None

    def price_to_usd(v: Optional[str]) -> Optional[int]:
        val = _int(v)
        if val is None:
            return None
        if price_currency == "uah":
            return max(1, round(val / usd_rate))
        return val

    return BikeFilters(
        brand=brand.strip() if brand and brand.strip() else None,
        min_price=price_to_usd(min_price),
        max_price=price_to_usd(max_price),
        min_year=_int(min_year),
        max_year=_int(max_year),
        condition=condition.strip() if condition and condition.strip() else None,
        available_only=available_only,
        min_mileage=_int(min_mileage),
        max_mileage=_int(max_mileage),
        min_engine=_int(min_engine),
        max_engine=_int(max_engine),
        sort=sort,
    )


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
