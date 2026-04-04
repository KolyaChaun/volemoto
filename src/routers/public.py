from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from src.core.config import templates
from src.db.database import get_db
from src.models.bike import Bike
from src.models.brand import Brand

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    motos  = db.query(Bike).filter_by(category="moto").limit(6).all()
    mopeds = db.query(Bike).filter_by(category="moped").limit(6).all()
    quads  = db.query(Bike).filter_by(category="quad").limit(6).all()
    return templates.TemplateResponse(request, "pages/index.html", {
        "motos": motos, "mopeds": mopeds, "quads": quads,
    })


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
):
    if category not in ("moto", "moped", "quad"):
        raise HTTPException(status_code=404)

    def to_int(v): return int(v) if v and v.strip() else None
    min_price_v   = to_int(min_price)
    max_price_v   = to_int(max_price)
    min_year_v    = to_int(min_year)
    max_year_v    = to_int(max_year)
    min_mileage_v = to_int(min_mileage)
    max_mileage_v = to_int(max_mileage)
    min_engine_v  = to_int(min_engine)
    max_engine_v  = to_int(max_engine)
    brand_v     = brand.strip()     if brand     and brand.strip()     else None
    condition_v = condition.strip() if condition and condition.strip() else None
    avail_v     = available_only in ("true", "on", "1", True)

    q = db.query(Bike).filter(Bike.category == category)

    if brand_v:                   q = q.filter(Bike.brand     == brand_v)
    if min_price_v:               q = q.filter(Bike.price     >= min_price_v)
    if max_price_v:               q = q.filter(Bike.price     <= max_price_v)
    if min_year_v:                q = q.filter(Bike.year      >= min_year_v)
    if max_year_v:                q = q.filter(Bike.year      <= max_year_v)
    if condition_v:               q = q.filter(Bike.condition == condition_v)
    if avail_v:                   q = q.filter(Bike.available == True)
    if min_mileage_v is not None: q = q.filter(Bike.mileage  >= min_mileage_v)
    if max_mileage_v is not None: q = q.filter(Bike.mileage  <= max_mileage_v)
    if min_engine_v  is not None: q = q.filter(Bike.engine   >= min_engine_v)
    if max_engine_v  is not None: q = q.filter(Bike.engine   <= max_engine_v)

    if sort == "price_asc":    q = q.order_by(Bike.price.asc())
    elif sort == "price_desc": q = q.order_by(Bike.price.desc())
    elif sort == "year_desc":  q = q.order_by(Bike.year.desc())
    elif sort == "year_asc":   q = q.order_by(Bike.year.asc())
    elif sort == "mileage":    q = q.order_by(Bike.mileage.asc())
    else:                      q = q.order_by(Bike.id.desc())

    bikes       = q.all()
    brands_list = [b.name for b in db.query(Brand).order_by(Brand.name).all()]
    conditions  = ["Відмінний", "Дуже добрий", "Добрий", "Задовільний"]
    cat_labels  = {"moto": "Мотоцикли", "moped": "Мопеди", "quad": "Квадроцикли"}

    return templates.TemplateResponse(request, "pages/catalog.html", {
        "bikes": bikes, "category": category, "cat_label": cat_labels[category],
        "brands": brands_list, "conditions": conditions, "sort": sort,
        "brand": brand_v, "condition": condition_v, "available_only": avail_v,
        "min_price": min_price_v, "max_price": max_price_v,
        "min_year":  min_year_v,  "max_year":  max_year_v,
        "min_mileage": min_mileage_v, "max_mileage": max_mileage_v,
        "min_engine":  min_engine_v,  "max_engine":  max_engine_v,
        "total": len(bikes),
    })


@router.get("/bike/{bike_id}", response_class=HTMLResponse)
def bike_detail(request: Request, bike_id: int, db: Session = Depends(get_db)):
    bike = db.query(Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Не знайдено")
    similar = db.query(Bike).filter(
        Bike.category == bike.category,
        Bike.id != bike.id
    ).limit(3).all()
    return templates.TemplateResponse(request, "pages/bike_detail.html", {
        "bike": bike, "similar": similar,
    })


@router.get("/brands", response_class=HTMLResponse)
def brands_page(request: Request, db: Session = Depends(get_db)):
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(request, "pages/brands.html", {"brands": brands})


@router.get("/contacts", response_class=HTMLResponse)
def contacts_page(request: Request):
    return templates.TemplateResponse(request, "pages/contacts.html", {})


@router.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    q = q.strip()
    bikes = []
    if q:
        term  = f"%{q.lower()}%"
        bikes = db.query(Bike).filter(
            Bike.name.ilike(term)    |
            Bike.brand.ilike(term)   |
            Bike.model.ilike(term)   |
            Bike.article.ilike(term) |
            Bike.color.ilike(term)
        ).order_by(Bike.id.desc()).all()
    return templates.TemplateResponse(request, "pages/search.html", {
        "bikes": bikes, "q": q, "total": len(bikes),
    })


@router.get("/api/search")
def api_search(q: str = "", db: Session = Depends(get_db)):
    if len(q.strip()) < 2:
        return JSONResponse([])
    term  = f"%{q.strip().lower()}%"
    bikes = db.query(Bike).filter(
        Bike.name.ilike(term)    |
        Bike.brand.ilike(term)   |
        Bike.model.ilike(term)   |
        Bike.article.ilike(term)
    ).limit(7).all()
    return JSONResponse([{
        "id": b.id, "name": b.name, "brand": b.brand,
        "year": b.year, "price": b.price,
        "photo": b.photo, "article": b.article,
    } for b in bikes])
