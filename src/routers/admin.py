from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from src.core.config import templates
from src.core.security import require_admin
from src.db.database import get_db
from src.models.admin import Admin
from src.models.bike import Bike, BikePhoto
from src.models.brand import Brand
from src.models.review import Review
from src.models.hero_slide import HeroSlide
from src.services.bike_service import gen_article
from src.services.file_service import save_photos, save_single_file, delete_file_by_path
from src.services.utils import unread_count

router = APIRouter(prefix="/admin")


@router.get("", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    bikes  = db.query(Bike).order_by(Bike.id.desc()).all()
    total  = len(bikes)
    avail  = len([b for b in bikes if b.available])
    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "total":   total,
        "motos":   len([b for b in bikes if b.category == "moto"]),
        "mopeds":  len([b for b in bikes if b.category == "moped"]),
        "quads":   len([b for b in bikes if b.category == "quad"]),
        "avail":   avail,
        "sold":    total - avail,
        "reviews": db.query(Review).count(),
        "recent":  bikes[:6],
        "unread":  unread_count(db),
    })


@router.get("/catalog", response_class=HTMLResponse)
def catalog(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    bikes = db.query(Bike).order_by(Bike.id.desc()).all()
    total = len(bikes)
    return templates.TemplateResponse(request, "admin/catalog.html", {
        "bikes":  bikes,
        "total":  total,
        "motos":  len([b for b in bikes if b.category == "moto"]),
        "mopeds": len([b for b in bikes if b.category == "moped"]),
        "quads":  len([b for b in bikes if b.category == "quad"]),
        "unread": unread_count(db),
    })


@router.get("/add", response_class=HTMLResponse)
def add_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(request, "admin/add_moto.html", {
        "bike": None, "action": "/admin/add",
        "brands": brands, "unread": unread_count(db),
    })


@router.post("/add")
async def add_bike(
    request: Request,
    name: str = Form(...), brand: str = Form(...), model: str = Form(...),
    year: int = Form(...), price: int = Form(...), mileage: int = Form(...),
    engine: int = Form(...), category: str = Form(...), color: str = Form(...),
    condition: str = Form(...), description: str = Form(""),
    youtube_url: str = Form(""),
    status: str = Form("available"), photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    paths = save_photos(photos or [], category)
    bike  = Bike(
        article=gen_article(db),
        name=name, brand=brand, model=model, year=year,
        price=price, mileage=mileage, engine=engine,
        category=category, color=color, condition=condition,
        description=description, available=(status == "available"),
        status=status, youtube_url=youtube_url,
        photo=paths[0] if paths else "",
    )
    db.add(bike)
    db.flush()
    for p in paths:
        db.add(BikePhoto(bike_id=bike.id, path=p))
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@router.get("/edit/{bike_id}", response_class=HTMLResponse)
def edit_page(
    request: Request, bike_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    bike = db.query(Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(404)
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(request, "admin/add_moto.html", {
        "bike": bike, "action": f"/admin/edit/{bike_id}",
        "brands": brands, "unread": unread_count(db),
    })


@router.post("/edit/{bike_id}")
async def edit_bike(
    request: Request, bike_id: int,
    name: str = Form(...), brand: str = Form(...), model: str = Form(...),
    year: int = Form(...), price: int = Form(...), mileage: int = Form(...),
    engine: int = Form(...), category: str = Form(...), color: str = Form(...),
    condition: str = Form(...), description: str = Form(""),
    youtube_url: str = Form(""),
    status: str = Form("available"), photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    bike = db.query(Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(404)
    new_paths = save_photos(photos or [], category)
    for p in new_paths:
        db.add(BikePhoto(bike_id=bike.id, path=p))
    bike.name = name;     bike.brand = brand;     bike.model = model
    bike.year = year;     bike.price = price;     bike.mileage = mileage
    bike.engine = engine; bike.category = category; bike.color = color
    bike.condition = condition; bike.description = description
    bike.youtube_url = youtube_url
    bike.status = status
    bike.available = (status == "available")
    db.flush()
    all_paths = [p.path for p in db.query(BikePhoto).filter_by(bike_id=bike.id).all()]
    if not bike.photo or bike.photo not in all_paths:
        bike.photo = all_paths[0] if all_paths else ""
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@router.post("/delete/{bike_id}")
def delete_bike(
    request: Request, bike_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    bike = db.query(Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(404)
    for photo in db.query(BikePhoto).filter_by(bike_id=bike_id).all():
        delete_file_by_path(photo.path)
        db.delete(photo)
    db.delete(bike)
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@router.post("/photo/main/{photo_id}")
def set_main_photo(
    request: Request, photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    photo = db.query(BikePhoto).filter_by(id=photo_id).first()
    if not photo:
        raise HTTPException(404)
    bike = db.query(Bike).filter_by(id=photo.bike_id).first()
    bike.photo = photo.path
    db.commit()
    return RedirectResponse(f"/admin/edit/{photo.bike_id}", status_code=302)


@router.post("/photo/delete/{photo_id}")
def delete_photo(
    request: Request, photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    photo = db.query(BikePhoto).filter_by(id=photo_id).first()
    if not photo:
        raise HTTPException(404)
    bike_id = photo.bike_id
    delete_file_by_path(photo.path)
    db.delete(photo)
    db.flush()
    bike      = db.query(Bike).filter_by(id=bike_id).first()
    all_paths = [p.path for p in db.query(BikePhoto).filter_by(bike_id=bike_id).all()]
    if not bike.photo or bike.photo not in all_paths:
        bike.photo = all_paths[0] if all_paths else ""
    db.commit()
    return RedirectResponse(f"/admin/edit/{bike_id}", status_code=302)


# ── Brands ────────────────────────────────────────────

@router.get("/brands", response_class=HTMLResponse)
def brands_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(request, "admin/add_brands.html", {
        "brands": brands, "unread": unread_count(db),
    })


@router.post("/brands/add")
async def add_brand(
    request: Request,
    name: str = Form(...),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    name = name.strip()
    if not name or db.query(Brand).filter_by(name=name).first():
        return RedirectResponse("/admin/brands", status_code=302)
    logo_path = save_single_file(logo, "brands") if logo else ""
    db.add(Brand(name=name, logo=logo_path))
    db.commit()
    return RedirectResponse("/admin/brands", status_code=302)


@router.post("/brands/delete/{brand_id}")
def delete_brand(
    request: Request, brand_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    brand = db.query(Brand).filter_by(id=brand_id).first()
    if brand:
        delete_file_by_path(brand.logo)
        db.delete(brand)
        db.commit()
    return RedirectResponse("/admin/brands", status_code=302)


# ── Hero slides ───────────────────────────────────────

@router.get("/hero", response_class=HTMLResponse)
def hero_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    slides = db.query(HeroSlide).order_by(HeroSlide.sort_order, HeroSlide.id).all()
    return templates.TemplateResponse(request, "admin/hero.html", {
        "slides": slides,
        "unread": unread_count(db),
    })


@router.post("/hero/upload")
async def hero_upload(
    request: Request,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    max_order = db.query(HeroSlide).count()
    for i, f in enumerate(files):
        if not f or not f.filename:
            continue
        path = save_single_file(f, "hero")
        db.add(HeroSlide(path=path, sort_order=max_order + i))
    db.commit()
    return RedirectResponse("/admin/hero", status_code=302)


@router.post("/hero/delete/{slide_id}")
def hero_delete(
    request: Request, slide_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    slide = db.query(HeroSlide).filter_by(id=slide_id).first()
    if slide:
        delete_file_by_path(slide.path)
        db.delete(slide)
        db.commit()
    return RedirectResponse("/admin/hero", status_code=302)