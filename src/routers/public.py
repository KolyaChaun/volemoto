from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from src.core.config import templates
from src.db.database import get_db
from src.models.bike import Bike
from src.models.brand import Brand
from src.models.hero_slide import HeroSlide
from src.models.review import Review
from src.models.product import Product

router = APIRouter()


FALLBACK_SLIDES = [
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1400&q=80",
    "https://images.unsplash.com/photo-1449426468159-d96dbf08f19f?w=1400&q=80",
    "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=1400&q=80",
    "https://images.unsplash.com/photo-1609630875171-b1321377ee65?w=1400&q=80",
    "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?w=1400&q=80",
]


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    motos  = db.query(Bike).filter_by(category="moto").limit(6).all()
    mopeds = db.query(Bike).filter_by(category="moped").limit(6).all()
    quads  = db.query(Bike).filter_by(category="quad").limit(6).all()
    slides = db.query(HeroSlide).order_by(HeroSlide.sort_order, HeroSlide.id).all()
    slide_urls = [s.path for s in slides] if slides else FALLBACK_SLIDES
    recent_reviews = db.query(Review).order_by(Review.id.desc()).limit(4).all()
    return templates.TemplateResponse(request, "pages/index.html", {
        "motos": motos, "mopeds": mopeds, "quads": quads,
        "slide_urls": slide_urls,
        "recent_reviews": recent_reviews,
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
    if category not in ("moto", "moped", "quad", "helmets", "gloves", "gear", "parts_new", "parts_used"):
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
    cat_labels  = {
        "moto": "Мотоцикли", "moped": "Мопеди", "quad": "Квадроцикли",
        "helmets": "Мотошоломи", "gloves": "Рукавиці", "gear": "Екіпіровка",
        "parts_new": "Запчастини нові", "parts_used": "Запчастини б/у",
    }

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


@router.get("/bike/{slug}", response_class=HTMLResponse)
def bike_detail_old(slug: str):
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/catalog/moto/{slug}", status_code=301)


@router.get("/catalog/{category}/{slug}", response_class=HTMLResponse)
def bike_detail(request: Request, category: str, slug: str, db: Session = Depends(get_db)):
    if category not in ("moto", "moped", "quad"):
        raise HTTPException(status_code=404)
    try:
        bike_id = int(slug.rsplit('_', 1)[-1])
    except (ValueError, IndexError):
        raise HTTPException(status_code=404, detail="Не знайдено")
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


EQUIPMENT_CATS = {
    "helmets": "Мотошоломи",
    "gloves":  "Рукавиці",
    "gear":    "Екіпіровка",
}
PARTS_CATS = {
    "parts_new":  "Запчастини нові",
    "parts_used": "Запчастини б/у",
}

PARTS_SUBCATS = [
    {"key": "oils",        "label": "Масла і Змазки",         "children": [
        {"key": "fork_oil",    "label": "Вилкові Масла"},
        {"key": "engine_oil",  "label": "Моторні масла"},
    ]},
    {"key": "maintenance", "label": "Для ТО",                 "children": [
        {"key": "brake_pads",  "label": "Колодки"},
        {"key": "seals",       "label": "Сальники/Пильники"},
        {"key": "spark_plugs", "label": "Свічки запалювання"},
        {"key": "air_filters", "label": "Повітряні Фільтри"},
    ]},
    {"key": "intake",      "label": "Впускна система",        "children": [
        {"key": "carburetor",       "label": "Карбюратор"},
        {"key": "fuel_system",      "label": "Паливна система"},
        {"key": "intake_manifold",  "label": "Впускний колектор"},
    ]},
    {"key": "suspension",  "label": "Підвіска",               "children": []},
    {"key": "brakes",      "label": "Гальмівна система",      "children": []},
    {"key": "electronics", "label": "Електроніка",            "children": [
        {"key": "batteries",   "label": "Акумулятори"},
    ]},
    {"key": "engine",      "label": "Двигун та трансмісія",   "children": [
        {"key": "bearings",    "label": "Підшипники"},
        {"key": "gaskets",     "label": "Прокладки"},
        {"key": "belts",       "label": "Ремені"},
        {"key": "bushings",    "label": "Втулки"},
    ]},
    {"key": "controls",    "label": "Органи управління",      "children": [
        {"key": "levers",      "label": "Курки"},
        {"key": "grips",       "label": "Рукоятки"},
    ]},
]


@router.get("/equipment", response_class=HTMLResponse)
def equipment_page(
    request: Request,
    db: Session = Depends(get_db),
    cat: Optional[str] = None,
    sort: str = "newest",
    brand: List[str] = Query(default=[]),
    color: List[str] = Query(default=[]),
    size: List[str] = Query(default=[]),
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    condition: Optional[str] = None,
    available_only: Optional[str] = None,
):
    def to_int(v): return int(v) if v and v.strip() else None
    min_price_v = to_int(min_price)
    max_price_v = to_int(max_price)
    brands_v    = [b.strip() for b in brand if b and b.strip()]
    colors_v    = [c.strip() for c in color if c and c.strip()]
    sizes_v     = [s.strip() for s in size  if s and s.strip()]
    condition_v = condition.strip() if condition and condition.strip() else None
    avail_v     = available_only in ("true", "on", "1", True)
    cat_v       = cat if cat in EQUIPMENT_CATS else None

    def split_vals(s): return [x.strip() for x in (s or "").split(",") if x.strip()]

    all_q = db.query(Product).filter(Product.category.in_(list(EQUIPMENT_CATS.keys())))
    if cat_v: all_q = all_q.filter(Product.category == cat_v)

    q = all_q
    if brands_v:    q = q.filter(func.trim(Product.brand).in_(brands_v))
    if min_price_v: q = q.filter(Product.price >= min_price_v)
    if max_price_v: q = q.filter(Product.price <= max_price_v)
    if condition_v: q = q.filter(Product.condition == condition_v)
    if avail_v:     q = q.filter(Product.available == True)

    if sort == "price_asc":   q = q.order_by(Product.price.asc())
    elif sort == "price_desc": q = q.order_by(Product.price.desc())
    else:                      q = q.order_by(Product.id.desc())

    items = q.all()
    if colors_v: items = [i for i in items if any(c in split_vals(i.color) for c in colors_v)]
    if sizes_v:  items = [i for i in items if any(s in split_vals(i.size)  for s in sizes_v)]

    all_items  = all_q.all()
    all_brands = sorted({p.brand.strip() for p in all_items if p.brand and p.brand.strip()})
    all_colors = sorted({c for p in all_items for c in split_vals(p.color)})
    all_sizes  = sorted({s for p in all_items for s in split_vals(p.size)})

    brand_counts = {}
    for p in all_items:
        if p.brand:
            key = p.brand.strip()
            brand_counts[key] = brand_counts.get(key, 0) + 1
    color_counts = {}
    for p in all_items:
        for c in split_vals(p.color): color_counts[c] = color_counts.get(c, 0) + 1
    size_counts = {}
    for p in all_items:
        for s in split_vals(p.size): size_counts[s] = size_counts.get(s, 0) + 1

    return templates.TemplateResponse(request, "pages/equipment.html", {
        "items": items, "total": len(items),
        "cat": cat_v, "cats": EQUIPMENT_CATS,
        "sort": sort, "selected_brands": brands_v, "condition": condition_v,
        "selected_colors": colors_v, "selected_sizes": sizes_v,
        "available_only": avail_v,
        "min_price": min_price_v, "max_price": max_price_v,
        "brands": all_brands, "colors": all_colors, "sizes": all_sizes,
        "brand_counts": brand_counts, "color_counts": color_counts, "size_counts": size_counts,
        "conditions": ["Нове", "Відмінний", "Дуже добрий", "Добрий", "Задовільний"],
    })


@router.get("/parts", response_class=HTMLResponse)
def parts_page(
    request: Request,
    db: Session = Depends(get_db),
    cat: Optional[str] = None,
    sort: str = "newest",
    brand: List[str] = Query(default=[]),
    subcategory: Optional[str] = None,
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    condition: Optional[str] = None,
    available_only: Optional[str] = None,
):
    def to_int(v): return int(v) if v and v.strip() else None
    min_price_v  = to_int(min_price)
    max_price_v  = to_int(max_price)
    brands_v     = [b.strip() for b in brand if b and b.strip()]
    condition_v  = condition.strip() if condition and condition.strip() else None
    avail_v      = available_only in ("true", "on", "1", True)
    cat_v        = cat if cat in PARTS_CATS else None
    subcat_v     = subcategory.strip() if subcategory and subcategory.strip() else None

    # build flat map of all subcat keys for validation
    all_subcat_keys = {c["key"] for g in PARTS_SUBCATS for c in [g] + g["children"]}
    if subcat_v not in all_subcat_keys:
        subcat_v = None

    q = db.query(Product).filter(Product.category.in_(list(PARTS_CATS.keys())))
    if cat_v:      q = q.filter(Product.category == cat_v)
    if brands_v:   q = q.filter(Product.brand.in_(brands_v))
    if subcat_v:   q = q.filter(Product.subcategory == subcat_v)
    if min_price_v: q = q.filter(Product.price >= min_price_v)
    if max_price_v: q = q.filter(Product.price <= max_price_v)
    if condition_v: q = q.filter(Product.condition == condition_v)
    if avail_v:    q = q.filter(Product.available == True)

    if sort == "price_asc":    q = q.order_by(Product.price.asc())
    elif sort == "price_desc": q = q.order_by(Product.price.desc())
    else:                      q = q.order_by(Product.id.desc())

    items         = q.all()
    all_parts     = db.query(Product).filter(Product.category.in_(list(PARTS_CATS.keys())), Product.brand != "").all()
    all_brands    = sorted({p.brand for p in all_parts})
    brand_counts  = {}
    for p in all_parts:
        brand_counts[p.brand] = brand_counts.get(p.brand, 0) + 1

    # Only show subcategory groups that have at least one product
    used_subcats = {
        p.subcategory for p in
        db.query(Product).filter(
            Product.category.in_(list(PARTS_CATS.keys())),
            Product.subcategory != None,
            Product.subcategory != "",
        ).all()
        if p.subcategory
    }
    filtered_subcats = [
        {**g, "children": [c for c in g["children"] if c["key"] in used_subcats]}
        for g in PARTS_SUBCATS
        if g["key"] in used_subcats or any(c["key"] in used_subcats for c in g["children"])
    ]

    return templates.TemplateResponse(request, "pages/parts.html", {
        "items": items, "total": len(items),
        "cat": cat_v, "cats": PARTS_CATS,
        "sort": sort, "selected_brands": brands_v, "condition": condition_v,
        "available_only": avail_v, "subcategory": subcat_v,
        "min_price": min_price_v, "max_price": max_price_v,
        "brands": all_brands, "brand_counts": brand_counts,
        "parts_subcats": filtered_subcats,
        "conditions": ["Відмінний", "Дуже добрий", "Добрий", "Задовільний"],
    })


@router.get("/equipment/{slug}", response_class=HTMLResponse)
@router.get("/parts/{slug}", response_class=HTMLResponse)
def product_detail(request: Request, slug: str, db: Session = Depends(get_db)):
    try:
        product_id = int(slug.rsplit('_', 1)[-1])
    except (ValueError, IndexError):
        raise HTTPException(status_code=404)
    product = db.query(Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404)
    if product.subcategory:
        similar = db.query(Product).filter(
            Product.subcategory == product.subcategory,
            Product.id != product.id
        ).limit(3).all()
    else:
        similar = db.query(Product).filter(
            Product.category == product.category,
            Product.id != product.id
        ).limit(3).all()
    return templates.TemplateResponse(request, "pages/parts_detail.html", {
        "product": product, "similar": similar,
    })


@router.get("/brands", response_class=HTMLResponse)
def brands_page(request: Request, db: Session = Depends(get_db)):
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(request, "pages/brands.html", {"brands": brands})


@router.get("/contacts", response_class=HTMLResponse)
def contacts_page(request: Request):
    return templates.TemplateResponse(request, "pages/contacts.html", {})


_EQUIPMENT_CATS = {"helmets", "gloves", "gear"}

@router.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    q = q.strip()
    bikes = []
    products = []
    if q:
        term = f"%{q.lower()}%"
        bikes = db.query(Bike).filter(
            func.lower(Bike.name).like(term)    |
            func.lower(Bike.brand).like(term)   |
            func.lower(Bike.model).like(term)   |
            func.lower(Bike.article).like(term) |
            func.lower(Bike.color).like(term)
        ).order_by(Bike.id.desc()).all()
        q_lower = q.lower()
        all_products = db.query(Product).order_by(Product.id.desc()).all()
        products = [p for p in all_products if any(
            q_lower in (f or '').lower()
            for f in [p.name, p.brand, p.subcategory, p.article, p.compatibility, p.model]
        )]
    equipment = [p for p in products if p.category in _EQUIPMENT_CATS]
    parts     = [p for p in products if p.category not in _EQUIPMENT_CATS]
    total = len(bikes) + len(products)
    return templates.TemplateResponse(request, "pages/search.html", {
        "bikes": bikes, "equipment": equipment, "parts": parts, "q": q, "total": total,
    })



@router.get("/api/search")
def api_search(q: str = "", db: Session = Depends(get_db)):
    if len(q.strip()) < 2:
        return JSONResponse([])
    term = f"%{q.strip().lower()}%"
    bikes = db.query(Bike).filter(
        func.lower(Bike.name).like(term)    |
        func.lower(Bike.brand).like(term)   |
        func.lower(Bike.model).like(term)   |
        func.lower(Bike.article).like(term)
    ).limit(5).all()
    q_lower = q.strip().lower()
    all_products = db.query(Product).all()
    products = [p for p in all_products if any(
        q_lower in (f or '').lower()
        for f in [p.name, p.brand, p.subcategory, p.article, p.compatibility, p.model]
    )][:5]
    results = [{
        "type": "bike",
        "id": b.id, "slug": b.slug, "name": b.name, "brand": b.brand,
        "year": b.year, "price": b.price, "photo": b.photo, "article": b.article, "category": b.category,
    } for b in bikes] + [{
        "type": "product",
        "id": p.id, "slug": p.slug, "name": p.name, "brand": p.brand,
        "category": p.category, "price": p.price, "photo": p.photo, "article": p.article,
    } for p in products]
    return JSONResponse(results)
