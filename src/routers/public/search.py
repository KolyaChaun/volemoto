from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.constants import GEAR_CATEGORIES
from src.core.config import templates
from src.db.database import get_db
from src.models.bike import Bike
from src.models.product import Product

router = APIRouter(tags=["Сайт — пошук"])


@router.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    q = q.strip()
    bikes, products = [], []
    if q:
        term = f"%{q.lower()}%"
        bikes = (
            db.query(Bike)
            .filter(
                func.lower(Bike.name).like(term)
                | func.lower(Bike.brand).like(term)
                | func.lower(Bike.model).like(term)
                | func.lower(Bike.article).like(term)
                | func.lower(Bike.color).like(term)
            )
            .order_by(Bike.id.desc())
            .all()
        )
        q_lower = q.lower()
        products = [
            p
            for p in db.query(Product).order_by(Product.id.desc()).all()
            if any(
                q_lower in (f or "").lower()
                for f in [
                    p.name,
                    p.brand,
                    p.subcategory,
                    p.article,
                    p.compatibility,
                    p.model,
                ]
            )
        ]
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
    term = f"%{q.strip().lower()}%"
    bikes = (
        db.query(Bike)
        .filter(
            func.lower(Bike.name).like(term)
            | func.lower(Bike.brand).like(term)
            | func.lower(Bike.model).like(term)
            | func.lower(Bike.article).like(term)
        )
        .limit(5)
        .all()
    )
    q_lower = q.strip().lower()
    products = [
        p
        for p in db.query(Product).all()
        if any(
            q_lower in (f or "").lower()
            for f in [
                p.name,
                p.brand,
                p.subcategory,
                p.article,
                p.compatibility,
                p.model,
            ]
        )
    ][:5]
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
