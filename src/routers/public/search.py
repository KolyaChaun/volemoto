from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.constants import GEAR_CATEGORIES
from src.core.config import templates
from src.core.search_utils import has_cyrillic, normalize_query
from src.db.database import get_db
from src.models.bike import Bike
from src.models.product import Product
from src.services.currency_service import uah_price

router = APIRouter(tags=["Сайт — пошук"])

_WORD_SIM_THRESHOLD = 0.4


def _bike_conditions(terms: list[str], fuzzy_terms: list[str]):
    conditions = []
    for term in terms:
        like = f"%{term}%"
        conditions.extend(
            [
                func.lower(Bike.name).like(like),
                func.lower(Bike.brand).like(like),
                func.lower(Bike.model).like(like),
                func.lower(Bike.article).like(like),
                func.lower(Bike.color).like(like),
            ]
        )
    for term in fuzzy_terms:
        bike_text = func.lower(
            func.coalesce(Bike.brand, "")
            + " "
            + func.coalesce(Bike.name, "")
            + " "
            + func.coalesce(Bike.model, "")
        )
        conditions.append(func.word_similarity(term, bike_text) > _WORD_SIM_THRESHOLD)
    return or_(*conditions)


def _product_conditions(terms: list[str], fuzzy_terms: list[str]):
    conditions = []
    for term in terms:
        like = f"%{term}%"
        conditions.extend(
            [
                func.lower(Product.name).like(like),
                func.lower(Product.brand).like(like),
                func.lower(Product.model).like(like),
                func.lower(Product.article).like(like),
                func.lower(Product.compatibility).like(like),
                func.lower(Product.subcategory).like(like),
            ]
        )
    for term in fuzzy_terms:
        product_text = func.lower(
            func.coalesce(Product.brand, "")
            + " "
            + func.coalesce(Product.name, "")
            + " "
            + func.coalesce(Product.model, "")
        )
        conditions.append(func.word_similarity(term, product_text) > _WORD_SIM_THRESHOLD)
    return or_(*conditions)


@router.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    q = q.strip()
    bikes, products = [], []
    if q:
        terms = normalize_query(q)
        fuzzy = [t for t in terms if not has_cyrillic(t)] if has_cyrillic(q) else []
        bikes = (
            db.query(Bike)
            .filter(_bike_conditions(terms, fuzzy))
            .order_by(Bike.id.desc())
            .all()
        )
        products = (
            db.query(Product)
            .filter(_product_conditions(terms, fuzzy))
            .order_by(Product.id.desc())
            .all()
        )
    equipment = [p for p in products if p.category in GEAR_CATEGORIES]
    parts = [p for p in products if p.category not in GEAR_CATEGORIES]
    return templates.TemplateResponse(
        request,
        "pages/search.html",
        {
            "bikes": bikes,
            "equipment": equipment,
            "parts": parts,
            "q": q,
            "total": len(bikes) + len(products),
        },
    )


@router.get("/api/search")
def api_search(q: str = "", db: Session = Depends(get_db)):
    if len(q.strip()) < 2:
        return JSONResponse([])

    terms = normalize_query(q)
    fuzzy = [t for t in terms if not has_cyrillic(t)] if has_cyrillic(q) else []
    bikes = (
        db.query(Bike)
        .filter(_bike_conditions(terms, fuzzy))
        .order_by(Bike.id.desc())
        .limit(5)
        .all()
    )
    products = (
        db.query(Product)
        .filter(_product_conditions(terms, fuzzy))
        .order_by(Product.id.desc())
        .limit(5)
        .all()
    )
    return JSONResponse(
        [
            {
                "type": "bike",
                "id": b.id,
                "slug": b.slug,
                "name": b.name,
                "brand": b.brand,
                "year": b.year,
                "price": b.price,
                "price_uah": uah_price(b.price),
                "photo": b.photo,
                "article": b.article,
                "category": b.category,
            }
            for b in bikes
        ]
        + [
            {
                "type": "product",
                "id": p.id,
                "slug": p.slug,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "price": p.price,
                "photo": p.photo,
                "article": p.article,
            }
            for p in products
        ]
    )
