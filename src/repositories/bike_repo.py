from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from src.models.bike import Bike, BikePhoto
from src.models.brand import Brand


@dataclass
class BikeFilters:
    brand: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    condition: Optional[str] = None
    available_only: bool = False
    min_mileage: Optional[int] = None
    max_mileage: Optional[int] = None
    min_engine: Optional[int] = None
    max_engine: Optional[int] = None
    sort: str = "newest"


_SORT_MAP = {
    "price_asc": Bike.price.asc(),
    "price_desc": Bike.price.desc(),
    "year_desc": Bike.year.desc(),
    "year_asc": Bike.year.asc(),
    "mileage": Bike.mileage.asc(),
}


class BikeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, bike_id: int) -> Bike | None:
        return self.db.get(Bike, bike_id)

    def list_all(self) -> list[Bike]:
        return self.db.query(Bike).order_by(Bike.id.desc()).all()

    def get_filtered(self, category: str, filters: BikeFilters) -> list[Bike]:
        q = self.db.query(Bike).filter(Bike.category == category)
        if filters.brand:
            q = q.filter(Bike.brand == filters.brand)
        if filters.min_price:
            q = q.filter(Bike.price >= filters.min_price)
        if filters.max_price:
            q = q.filter(Bike.price <= filters.max_price)
        if filters.min_year:
            q = q.filter(Bike.year >= filters.min_year)
        if filters.max_year:
            q = q.filter(Bike.year <= filters.max_year)
        if filters.condition:
            q = q.filter(Bike.condition == filters.condition)
        if filters.available_only:
            q = q.filter(Bike.available == True)  # noqa: E712
        if filters.min_mileage is not None:
            q = q.filter(Bike.mileage >= filters.min_mileage)
        if filters.max_mileage is not None:
            q = q.filter(Bike.mileage <= filters.max_mileage)
        if filters.min_engine is not None:
            q = q.filter(Bike.engine >= filters.min_engine)
        if filters.max_engine is not None:
            q = q.filter(Bike.engine <= filters.max_engine)
        return q.order_by(_SORT_MAP.get(filters.sort, Bike.id.desc())).all()

    def brands_list(self) -> list[str]:
        return [b.name for b in self.db.query(Brand).order_by(Brand.name).all()]

    def article_exists(self, article: str) -> bool:
        return self.db.query(Bike).filter_by(article=article).first() is not None

    def save(self, bike: Bike, photo_paths: list[str] = ()) -> Bike:
        self.db.add(bike)
        self.db.flush()
        for path in photo_paths:
            self.db.add(BikePhoto(bike_id=bike.id, path=path))
        self.db.commit()
        return bike

    def add_photos(self, bike_id: int, paths: list[str]) -> None:
        for path in paths:
            self.db.add(BikePhoto(bike_id=bike_id, path=path))

    def photo_paths(self, bike_id: int) -> list[str]:
        return [
            p.path for p in self.db.query(BikePhoto).filter_by(bike_id=bike_id).all()
        ]

    def get_photo(self, photo_id: int) -> BikePhoto | None:
        return self.db.get(BikePhoto, photo_id)

    def delete_photo(self, photo: BikePhoto) -> None:
        self.db.delete(photo)

    def delete(self, bike: Bike) -> None:
        self.db.delete(bike)
        self.db.commit()

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()
