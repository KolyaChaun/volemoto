from typing import Optional

from sqlalchemy.orm import Session

from src.models.bike import Bike
from src.repositories.bike_repo import BikeFilters, BikeRepository
from src.services.base_item_service import BaseItemService
from src.services.currency_service import get_cached_rate


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


class BikeService(BaseItemService[Bike]):
    _owner_id_attr = "bike_id"

    def _make_repo(self, db: Session) -> BikeRepository:
        return BikeRepository(db)

    def _make_model(self, article: str, photo: str, data: dict) -> Bike:
        return Bike(article=article, photo=photo, **data)
