from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
import shutil, os, uuid, random

from database import get_db, engine
import models

models.Base.metadata.create_all(bind=engine)

# авто-міграції для нових колонок
from sqlalchemy import text, inspect as sa_inspect
def _add_column_if_missing(table, column, definition):
    with engine.connect() as conn:
        cols = [c["name"] for c in sa_inspect(engine).get_columns(table)]
        if column not in cols:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
            conn.commit()

_add_column_if_missing("brands", "logo", "VARCHAR(300) DEFAULT ''")
_add_column_if_missing("reviews", "is_read", "BOOLEAN DEFAULT FALSE")
_add_column_if_missing("bikes", "article", "VARCHAR(10) DEFAULT ''")

def _gen_article(db) -> str:
    while True:
        code = f"{random.randint(0, 999999):06d}"
        if not db.query(models.Bike).filter_by(article=code).first():
            return code

# заповнюємо артикули для існуючих мотоциклів без артикулу
def _fill_missing_articles():
    from database import SessionLocal
    db = SessionLocal()
    try:
        bikes = db.query(models.Bike).filter(
            (models.Bike.article == None) | (models.Bike.article == "")
        ).all()
        for bike in bikes:
            bike.article = _gen_article(db)
        if bikes:
            db.commit()
    finally:
        db.close()

_fill_missing_articles()

def _unread_count(db: Session) -> int:
    return db.query(models.Review).filter_by(is_read=False).count()

# створюємо таблицю reviews якщо ще не існує
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VOLE MOTO")

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/media", StaticFiles(directory="src/media"), name="media")

templates = Jinja2Templates(directory="src/templates")

load_dotenv()

ADMIN_LOGIN = os.getenv("ADMIN_LOGIN")
ADMIN_PASS = os.getenv("ADMIN_PASS")

def check_admin(request: Request):
    return request.cookies.get("admin") == "ok"

# ─── PUBLIC ───────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    motos  = db.query(models.Bike).filter_by(category="moto").limit(6).all()
    mopeds = db.query(models.Bike).filter_by(category="moped").limit(6).all()
    quads  = db.query(models.Bike).filter_by(category="quad").limit(6).all()
    return templates.TemplateResponse(request, "index.html", {
        "motos": motos, "mopeds": mopeds, "quads": quads,
    })

@app.get("/catalog/{category}", response_class=HTMLResponse)
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

    # конвертуємо порожні рядки в None
    def to_int(v): return int(v) if v and v.strip() else None
    min_price_v   = to_int(min_price)
    max_price_v   = to_int(max_price)
    min_year_v    = to_int(min_year)
    max_year_v    = to_int(max_year)
    min_mileage_v = to_int(min_mileage)
    max_mileage_v = to_int(max_mileage)
    min_engine_v  = to_int(min_engine)
    max_engine_v  = to_int(max_engine)
    brand_v      = brand.strip() if brand and brand.strip() else None
    condition_v  = condition.strip() if condition and condition.strip() else None
    avail_v      = available_only in ("true", "on", "1", True)

    q = db.query(models.Bike).filter(models.Bike.category == category)

    if brand_v:        q = q.filter(models.Bike.brand == brand_v)
    if min_price_v:    q = q.filter(models.Bike.price >= min_price_v)
    if max_price_v:    q = q.filter(models.Bike.price <= max_price_v)
    if min_year_v:     q = q.filter(models.Bike.year >= min_year_v)
    if max_year_v:     q = q.filter(models.Bike.year <= max_year_v)
    if condition_v:    q = q.filter(models.Bike.condition == condition_v)
    if avail_v:        q = q.filter(models.Bike.available == True)
    if min_mileage_v is not None: q = q.filter(models.Bike.mileage >= min_mileage_v)
    if max_mileage_v is not None: q = q.filter(models.Bike.mileage <= max_mileage_v)
    if min_engine_v is not None:  q = q.filter(models.Bike.engine >= min_engine_v)
    if max_engine_v is not None:  q = q.filter(models.Bike.engine <= max_engine_v)

    if sort == "price_asc":    q = q.order_by(models.Bike.price.asc())
    elif sort == "price_desc": q = q.order_by(models.Bike.price.desc())
    elif sort == "year_desc":  q = q.order_by(models.Bike.year.desc())
    elif sort == "year_asc":   q = q.order_by(models.Bike.year.asc())
    elif sort == "mileage":    q = q.order_by(models.Bike.mileage.asc())
    else:                      q = q.order_by(models.Bike.id.desc())

    bikes = q.all()

    # дані для фільтрів — бренди з таблиці brands
    brands = [b.name for b in db.query(models.Brand).order_by(models.Brand.name).all()]
    conditions = ["Відмінний", "Дуже добрий", "Добрий", "Задовільний"]

    cat_labels = {"moto": "Мотоцикли", "moped": "Мопеди", "quad": "Квадроцикли"}

    return templates.TemplateResponse(request, "catalog.html", {
        "bikes": bikes,
        "category": category,
        "cat_label": cat_labels[category],
        "brands": brands,
        "conditions": conditions,
        "sort": sort,
        "brand": brand_v,
        "min_price": min_price_v,
        "max_price": max_price_v,
        "min_year": min_year_v,
        "max_year": max_year_v,
        "condition": condition_v,
        "available_only": avail_v,
        "min_mileage": min_mileage_v,
        "max_mileage": max_mileage_v,
        "min_engine": min_engine_v,
        "max_engine": max_engine_v,
        "total": len(bikes),
    })


@app.get("/bike/{bike_id}", response_class=HTMLResponse)
def bike_detail(request: Request, bike_id: int, db: Session = Depends(get_db)):
    bike = db.query(models.Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Не знайдено")
    similar = db.query(models.Bike).filter(
        models.Bike.category == bike.category,
        models.Bike.id != bike.id
    ).limit(3).all()
    return templates.TemplateResponse(request, "bike_detail.html", {
        "bike": bike, "similar": similar,
    })

# ─── ADMIN ────────────────────────────────────────

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(request, "admin/login.html", {"error": None})

@app.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_LOGIN and password == ADMIN_PASS:
        resp = RedirectResponse("/admin", status_code=302)
        resp.set_cookie("admin", "ok", httponly=True)
        return resp
    return templates.TemplateResponse(request, "admin/login.html", {
        "error": "Невірний логін або пароль"
    })

@app.get("/admin/logout")
def admin_logout():
    resp = RedirectResponse("/admin/login", status_code=302)
    resp.delete_cookie("admin")
    return resp

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    bikes   = db.query(models.Bike).order_by(models.Bike.id.desc()).all()
    total   = len(bikes)
    motos   = len([b for b in bikes if b.category == "moto"])
    mopeds  = len([b for b in bikes if b.category == "moped"])
    quads   = len([b for b in bikes if b.category == "quad"])
    avail   = len([b for b in bikes if b.available])
    sold    = total - avail
    reviews = db.query(models.Review).count()
    unread  = _unread_count(db)
    recent  = bikes[:6]
    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "total": total, "motos": motos, "mopeds": mopeds, "quads": quads,
        "avail": avail, "sold": sold, "reviews": reviews,
        "recent": recent, "unread": unread,
    })

@app.get("/admin/catalog", response_class=HTMLResponse)
def admin_catalog(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    bikes  = db.query(models.Bike).order_by(models.Bike.id.desc()).all()
    total  = len(bikes)
    motos  = len([b for b in bikes if b.category == "moto"])
    mopeds = len([b for b in bikes if b.category == "moped"])
    quads  = len([b for b in bikes if b.category == "quad"])
    return templates.TemplateResponse(request, "admin/catalog.html", {
        "bikes": bikes, "total": total,
        "motos": motos, "mopeds": mopeds, "quads": quads,
        "unread": _unread_count(db),
    })

@app.get("/admin/add", response_class=HTMLResponse)
def admin_add_page(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    brands = db.query(models.Brand).order_by(models.Brand.name).all()
    return templates.TemplateResponse(request, "admin/add_moto.html", {
        "bike": None, "action": "/admin/add", "brands": brands, "unread": _unread_count(db),
    })

CATEGORY_FOLDER = {"moto": "moto", "moped": "moped", "quad": "quad"}

def save_photos(files: List[UploadFile], category: str = "moto") -> List[str]:
    folder = CATEGORY_FOLDER.get(category, "moto")
    dir_path = f"src/media/{folder}"
    os.makedirs(dir_path, exist_ok=True)
    paths = []
    for f in files:
        if f and f.filename:
            ext = f.filename.rsplit(".", 1)[-1]
            filename = f"{uuid.uuid4().hex}.{ext}"
            with open(f"{dir_path}/{filename}", "wb") as out:
                shutil.copyfileobj(f.file, out)
            paths.append(f"/media/{folder}/{filename}")
    return paths


@app.post("/admin/add")
async def admin_add(
    request: Request,
    name: str = Form(...), brand: str = Form(...), model: str = Form(...),
    year: int = Form(...), price: int = Form(...), mileage: int = Form(...),
    engine: int = Form(...), category: str = Form(...), color: str = Form(...),
    condition: str = Form(...), description: str = Form(""),
    available: bool = Form(True), photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)

    paths = save_photos(photos or [], category)
    bike = models.Bike(
        article=_gen_article(db),
        name=name, brand=brand, model=model, year=year,
        price=price, mileage=mileage, engine=engine,
        category=category, color=color, condition=condition,
        description=description, available=available,
        photo=paths[0] if paths else "",
    )
    db.add(bike)
    db.flush()
    for p in paths:
        db.add(models.BikePhoto(bike_id=bike.id, path=p))
    db.commit()
    return RedirectResponse("/admin", status_code=302)

@app.get("/admin/edit/{bike_id}", response_class=HTMLResponse)
def admin_edit_page(request: Request, bike_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    bike = db.query(models.Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(404)
    brands = db.query(models.Brand).order_by(models.Brand.name).all()
    return templates.TemplateResponse(request, "admin/add_moto.html", {
        "bike": bike, "action": f"/admin/edit/{bike_id}", "brands": brands,
        "unread": _unread_count(db),
    })

@app.post("/admin/edit/{bike_id}")
async def admin_edit(
    request: Request, bike_id: int,
    name: str = Form(...), brand: str = Form(...), model: str = Form(...),
    year: int = Form(...), price: int = Form(...), mileage: int = Form(...),
    engine: int = Form(...), category: str = Form(...), color: str = Form(...),
    condition: str = Form(...), description: str = Form(""),
    available: Optional[str] = Form(None), photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    bike = db.query(models.Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(404)

    new_paths = save_photos(photos or [], category)
    for p in new_paths:
        db.add(models.BikePhoto(bike_id=bike.id, path=p))

    bike.name = name; bike.brand = brand; bike.model = model
    bike.year = year; bike.price = price; bike.mileage = mileage
    bike.engine = engine; bike.category = category; bike.color = color
    bike.condition = condition; bike.description = description
    bike.available = available is not None
    db.flush()
    # головне фото = перше з таблиці фото
    first = db.query(models.BikePhoto).filter_by(bike_id=bike.id).first()
    bike.photo = first.path if first else ""
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@app.post("/admin/photo/delete/{photo_id}")
def admin_photo_delete(request: Request, photo_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    photo = db.query(models.BikePhoto).filter_by(id=photo_id).first()
    if not photo:
        raise HTTPException(404)
    bike_id = photo.bike_id
    # видаляємо файл з диску
    disk_path = "src" + photo.path
    if os.path.exists(disk_path):
        os.remove(disk_path)
    db.delete(photo)
    db.flush()
    # оновлюємо головне фото
    bike = db.query(models.Bike).filter_by(id=bike_id).first()
    first = db.query(models.BikePhoto).filter_by(bike_id=bike_id).first()
    bike.photo = first.path if first else ""
    db.commit()
    return RedirectResponse(f"/admin/edit/{bike_id}", status_code=302)

@app.post("/admin/delete/{bike_id}")
def admin_delete(request: Request, bike_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    bike = db.query(models.Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(404)
    photos = db.query(models.BikePhoto).filter_by(bike_id=bike_id).all()

    for photo in photos:
        disk_path = "src" + photo.path
        if os.path.exists(disk_path):
            os.remove(disk_path)
        db.delete(photo)

    db.delete(bike)
    db.commit()

    return RedirectResponse("/admin", status_code=302)

# ─── BRANDS ───────────────────────────────────────

@app.get("/admin/brands", response_class=HTMLResponse)
def admin_brands(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    brands = db.query(models.Brand).order_by(models.Brand.name).all()
    return templates.TemplateResponse(request, "admin/add_brands.html", {"brands": brands, "unread": _unread_count(db)})

@app.post("/admin/brands/add")
async def admin_brands_add(
    request: Request,
    name: str = Form(...),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    name = name.strip()
    if not name or db.query(models.Brand).filter_by(name=name).first():
        return RedirectResponse("/admin/brands", status_code=302)
    logo_path = ""
    if logo and logo.filename:
        ext = logo.filename.rsplit(".", 1)[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        os.makedirs("src/media/brands", exist_ok=True)
        with open(f"src/media/brands/{filename}", "wb") as f:
            shutil.copyfileobj(logo.file, f)
        logo_path = f"/media/brands/{filename}"
    db.add(models.Brand(name=name, logo=logo_path))
    db.commit()
    return RedirectResponse("/admin/brands", status_code=302)

@app.post("/admin/brands/delete/{brand_id}")
def admin_brands_delete(request: Request, brand_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    brand = db.query(models.Brand).filter_by(id=brand_id).first()
    if brand:
        if brand.logo:
            disk = "src" + brand.logo
            if os.path.exists(disk):
                os.remove(disk)
        db.delete(brand)
        db.commit()
    return RedirectResponse("/admin/brands", status_code=302)

# ─── PUBLIC BRANDS PAGE ───────────────────────────

@app.get("/brands", response_class=HTMLResponse)
def brands_page(request: Request, db: Session = Depends(get_db)):
    brands = db.query(models.Brand).order_by(models.Brand.name).all()
    return templates.TemplateResponse(request, "brands.html", {"brands": brands})

@app.get("/api/search")
def api_search(q: str = "", db: Session = Depends(get_db)):
    from fastapi.responses import JSONResponse
    if len(q.strip()) < 2:
        return JSONResponse([])
    term = f"%{q.strip().lower()}%"
    bikes = db.query(models.Bike).filter(
        models.Bike.name.ilike(term) |
        models.Bike.brand.ilike(term) |
        models.Bike.model.ilike(term) |
        models.Bike.article.ilike(term)
    ).limit(7).all()
    return JSONResponse([{
        "id": b.id, "name": b.name, "brand": b.brand,
        "year": b.year, "price": b.price,
        "photo": b.photo, "article": b.article,
    } for b in bikes])

@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    q = q.strip()
    bikes = []
    if q:
        term = f"%{q.lower()}%"
        bikes = db.query(models.Bike).filter(
            models.Bike.name.ilike(term) |
            models.Bike.brand.ilike(term) |
            models.Bike.model.ilike(term) |
            models.Bike.article.ilike(term) |
            models.Bike.color.ilike(term)
        ).order_by(models.Bike.id.desc()).all()
    return templates.TemplateResponse(request, "search.html", {
        "bikes": bikes, "q": q, "total": len(bikes),
    })

@app.get("/contacts", response_class=HTMLResponse)
def contacts_page(request: Request):
    return templates.TemplateResponse(request, "contacts.html", {})

@app.get("/admin/reviews", response_class=HTMLResponse)
def admin_reviews(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    reviews = db.query(models.Review).order_by(models.Review.id.desc()).all()
    # позначаємо всі як прочитані
    db.query(models.Review).filter_by(is_read=False).update({"is_read": True})
    db.commit()
    return templates.TemplateResponse(request, "admin/reviews.html", {"reviews": reviews, "unread": 0})

@app.post("/admin/reviews/{review_id}/reply")
def admin_review_reply(request: Request, review_id: int, text: str = Form(...), db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    if text.strip():
        db.add(models.ReviewReply(review_id=review_id, name="VOLE MOTO", text=text.strip(), is_admin=True))
        db.commit()
    return RedirectResponse(f"/admin/reviews", status_code=302)

@app.post("/admin/reviews/{review_id}/delete")
def admin_review_delete(request: Request, review_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    review = db.query(models.Review).filter_by(id=review_id).first()
    if review:
        db.delete(review)
        db.commit()
    return RedirectResponse("/admin/reviews", status_code=302)

@app.post("/admin/reviews/reply/{reply_id}/delete")
def admin_reply_delete(request: Request, reply_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    reply = db.query(models.ReviewReply).filter_by(id=reply_id).first()
    if reply:
        db.delete(reply)
        db.commit()
    return RedirectResponse("/admin/reviews", status_code=302)

@app.get("/reviews", response_class=HTMLResponse)
def reviews_page(request: Request, sort: str = "new", limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(models.Review)
    if sort == "rating":
        q = q.order_by(models.Review.rating.desc())
    elif sort == "old":
        q = q.order_by(models.Review.id.asc())
    else:
        q = q.order_by(models.Review.id.desc())
    all_reviews = q.all()
    total = len(all_reviews)
    avg = round(sum(r.rating for r in all_reviews) / total, 1) if total else 0
    counts = {i: sum(1 for r in all_reviews if r.rating == i) for i in range(1, 6)}
    reviews = all_reviews[:limit]
    has_more = total > limit
    return templates.TemplateResponse(request, "reviews.html", {
        "reviews": reviews, "total": total, "avg": avg, "counts": counts,
        "sort": sort, "is_admin": check_admin(request),
        "limit": limit, "has_more": has_more,
    })

@app.post("/reviews")
def reviews_add(
    request: Request,
    name: str = Form(...),
    rating: int = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db),
):
    if 1 <= rating <= 5 and name.strip() and text.strip():
        db.add(models.Review(name=name.strip(), rating=rating, text=text.strip()))
        db.commit()
    return RedirectResponse("/reviews", status_code=302)

@app.post("/reviews/{review_id}/reply")
def review_user_reply(
    request: Request,
    review_id: int,
    name: str = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db),
):
    review = db.query(models.Review).filter_by(id=review_id).first()
    if review and name.strip() and text.strip():
        db.add(models.ReviewReply(review_id=review_id, name=name.strip(), text=text.strip(), is_admin=False))
        db.commit()
    return RedirectResponse("/reviews", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)