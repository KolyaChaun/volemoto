import os
from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, List

from src.core.config import templates
from src.core.security import check_admin
from src.db.database import get_db
from src.models.bike import Bike, BikePhoto
from src.models.brand import Brand
from src.models.review import Review
from src.services.bike_service import gen_article
from src.services.file_service import save_photos, save_single_file
from src.services.utils import unread_count

router = APIRouter(prefix="/admin")


@router.get("", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
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
def catalog(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
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
def add_page(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
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
    available: bool = Form(True), photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    paths = save_photos(photos or [], category)
    bike  = Bike(
        article=gen_article(db),
        name=name, brand=brand, model=model, year=year,
        price=price, mileage=mileage, engine=engine,
        category=category, color=color, condition=condition,
        description=description, available=available,
        photo=paths[0] if paths else "",
    )
    db.add(bike)
    db.flush()
    for p in paths:
        db.add(BikePhoto(bike_id=bike.id, path=p))
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@router.get("/edit/{bike_id}", response_class=HTMLResponse)
def edit_page(request: Request, bike_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
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
    available: Optional[str] = Form(None), photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
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
    bike.available = available is not None
    db.flush()
    all_paths = [p.path for p in db.query(BikePhoto).filter_by(bike_id=bike.id).all()]
    if not bike.photo or bike.photo not in all_paths:
        bike.photo = all_paths[0] if all_paths else ""
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@router.post("/delete/{bike_id}")
def delete_bike(request: Request, bike_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    bike = db.query(Bike).filter_by(id=bike_id).first()
    if not bike:
        raise HTTPException(404)
    for photo in db.query(BikePhoto).filter_by(bike_id=bike_id).all():
        disk_path = "src" + photo.path
        if os.path.exists(disk_path):
            os.remove(disk_path)
        db.delete(photo)
    db.delete(bike)
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@router.post("/photo/main/{photo_id}")
def set_main_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    photo = db.query(BikePhoto).filter_by(id=photo_id).first()
    if not photo:
        raise HTTPException(404)
    bike = db.query(Bike).filter_by(id=photo.bike_id).first()
    bike.photo = photo.path
    db.commit()
    return RedirectResponse(f"/admin/edit/{photo.bike_id}", status_code=302)


@router.post("/photo/delete/{photo_id}")
def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    photo = db.query(BikePhoto).filter_by(id=photo_id).first()
    if not photo:
        raise HTTPException(404)
    bike_id   = photo.bike_id
    disk_path = "src" + photo.path
    if os.path.exists(disk_path):
        os.remove(disk_path)
    db.delete(photo)
    db.flush()
    bike      = db.query(Bike).filter_by(id=bike_id).first()
    all_paths = [p.path for p in db.query(BikePhoto).filter_by(bike_id=bike_id).all()]
    if not bike.photo or bike.photo not in all_paths:
        bike.photo = all_paths[0] if all_paths else ""
    db.commit()
    return RedirectResponse(f"/admin/edit/{bike_id}", status_code=302)


@router.get("/brands", response_class=HTMLResponse)
def brands_page(request: Request, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
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
):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    name = name.strip()
    if not name or db.query(Brand).filter_by(name=name).first():
        return RedirectResponse("/admin/brands", status_code=302)
    logo_path = save_single_file(logo, "brands") if logo else ""
    db.add(Brand(name=name, logo=logo_path))
    db.commit()
    return RedirectResponse("/admin/brands", status_code=302)


@router.post("/brands/delete/{brand_id}")
def delete_brand(request: Request, brand_id: int, db: Session = Depends(get_db)):
    if not check_admin(request):
        return RedirectResponse("/admin/login", status_code=302)
    brand = db.query(Brand).filter_by(id=brand_id).first()
    if brand:
        if brand.logo:
            disk = "src" + brand.logo
            if os.path.exists(disk):
                os.remove(disk)
        db.delete(brand)
        db.commit()
    return RedirectResponse("/admin/brands", status_code=302)
