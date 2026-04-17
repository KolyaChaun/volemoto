from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.constants import (
    BIKE_CATEGORIES,
    BIKE_CONDITIONS,
    CATALOG_LABELS,
    PRODUCT_CATEGORIES,
)
from src.core.config import templates
from src.db.database import get_db
from src.models.bike import Bike
from src.repositories.bike_repo import BikeRepository
from src.services.bike_service import build_bike_filters, resolve_price_currency

router = APIRouter(tags=["Сайт — мотоцикли"])


def _to_int(v: Optional[str]) -> Optional[int]:
    return int(v) if v and v.strip() else None


def _flag(v: Optional[str]) -> bool:
    return v in ("true", "on", "1", True)


@router.get("/catalog/{category}", response_class=HTMLResponse)
def catalog(
    request: Request,
    category: str,
    db: Session = Depends(get_db),
    sort: str = "newest",
    brand: Optional[str] = None,
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    min_year: Optional[str] = None,
    max_year: Optional[str] = None,
    condition: Optional[str] = None,
    available_only: Optional[str] = None,
    min_mileage: Optional[str] = None,
    max_mileage: Optional[str] = None,
    min_engine: Optional[str] = None,
    max_engine: Optional[str] = None,
    price_currency: Optional[str] = "usd",
):
    if category not in (BIKE_CATEGORIES | set(PRODUCT_CATEGORIES)):
        raise HTTPException(status_code=404)

    currency, usd_rate, rate_available = resolve_price_currency(price_currency)
    filters = build_bike_filters(
        sort=sort,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year,
        condition=condition,
        available_only=_flag(available_only),
        min_mileage=min_mileage,
        max_mileage=max_mileage,
        min_engine=min_engine,
        max_engine=max_engine,
        price_currency=currency,
        usd_rate=usd_rate,
    )
    repo = BikeRepository(db)
    bikes = repo.get_filtered(category, filters)

    return templates.TemplateResponse(
        request,
        "pages/catalog.html",
        {
            "bikes": bikes,
            "category": category,
            "cat_label": CATALOG_LABELS.get(category, category),
            "brands": repo.brands_list(),
            "conditions": BIKE_CONDITIONS,
            "sort": sort,
            "brand": filters.brand,
            "condition": filters.condition,
            "available_only": filters.available_only,
            "min_price": _to_int(min_price),
            "max_price": _to_int(max_price),
            "price_currency": currency,
            "usd_rate": round(usd_rate, 2),
            "rate_available": rate_available,
            "min_year": filters.min_year,
            "max_year": filters.max_year,
            "min_mileage": filters.min_mileage,
            "max_mileage": filters.max_mileage,
            "min_engine": filters.min_engine,
            "max_engine": filters.max_engine,
            "total": len(bikes),
        },
    )


@router.get("/bike/{slug}", response_class=HTMLResponse)
def bike_detail_old(slug: str):
    return RedirectResponse(url=f"/catalog/moto/{slug}", status_code=301)


@router.get("/catalog/{category}/{slug}", response_class=HTMLResponse)
def bike_detail(
    request: Request, category: str, slug: str, db: Session = Depends(get_db)
):
    if category not in BIKE_CATEGORIES:
        raise HTTPException(status_code=404)
    try:
        bike_id = int(slug.rsplit("_", 1)[-1])
    except (ValueError, IndexError):
        raise HTTPException(status_code=404)
    bike = BikeRepository(db).get(bike_id)
    if not bike:
        raise HTTPException(status_code=404)
    similar = (
        db.query(Bike)
        .filter(Bike.category == bike.category, Bike.id != bike.id)
        .limit(3)
        .all()
    )
    return templates.TemplateResponse(
        request,
        "pages/bike_detail.html",
        {"bike": bike, "similar": similar},
    )
