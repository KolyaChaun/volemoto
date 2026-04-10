from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.config import templates
from src.core.security import require_admin
from src.db.database import get_db
from src.models.admin import Admin
from src.models.brand import Brand
from src.repositories.review_repo import ReviewRepository
from src.services.bike_service import BikeService

router = APIRouter(tags=["Адмін — мотоцикли"])


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    from src.models.bike import Bike
    from src.models.product import Product

    bikes = db.query(Bike).order_by(Bike.id.desc()).all()
    total = len(bikes)
    avail = sum(1 for b in bikes if b.available)
    products = db.query(Product).all()
    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {
            "total": total,
            "motos": sum(1 for b in bikes if b.category == "moto"),
            "mopeds": sum(1 for b in bikes if b.category == "moped"),
            "quads": sum(1 for b in bikes if b.category == "quad"),
            "avail": avail,
            "sold": total - avail,
            "gear_total": sum(
                1 for p in products if p.category in ("helmets", "gloves", "gear")
            ),
            "parts_total": sum(
                1 for p in products if p.category in ("parts_new", "parts_used")
            ),
            "reviews": ReviewRepository(db).unread_count(),
            "recent": bikes[:6],
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.get("/catalog", response_class=HTMLResponse)
def catalog(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    from src.models.bike import Bike

    bikes = db.query(Bike).order_by(Bike.id.desc()).all()
    total = len(bikes)
    return templates.TemplateResponse(
        request,
        "admin/catalog.html",
        {
            "bikes": bikes,
            "total": total,
            "motos": sum(1 for b in bikes if b.category == "moto"),
            "mopeds": sum(1 for b in bikes if b.category == "moped"),
            "quads": sum(1 for b in bikes if b.category == "quad"),
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.get("/add", response_class=HTMLResponse)
def add_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(
        request,
        "admin/add_moto.html",
        {
            "bike": None,
            "action": "/admin/add",
            "brands": brands,
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.post("/add")
async def add_bike(
    request: Request,
    name: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    price: int = Form(...),
    mileage: int = Form(...),
    engine: int = Form(...),
    category: str = Form(...),
    color: str = Form(...),
    condition: str = Form(...),
    description: str = Form(""),
    youtube_url: str = Form(""),
    status: str = Form("available"),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    BikeService(db).create(
        data={
            "name": name,
            "brand": brand,
            "model": model,
            "year": year,
            "price": price,
            "mileage": mileage,
            "engine": engine,
            "category": category,
            "color": color,
            "condition": condition,
            "description": description,
            "youtube_url": youtube_url,
            "available": status == "available",
            "status": status,
        },
        photo_files=photos or [],
    )
    return RedirectResponse("/admin", status_code=302)


@router.get("/edit/{bike_id}", response_class=HTMLResponse)
def edit_page(
    request: Request,
    bike_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    from src.repositories.bike_repo import BikeRepository

    bike = BikeRepository(db).get(bike_id)
    if not bike:
        raise HTTPException(404)
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(
        request,
        "admin/add_moto.html",
        {
            "bike": bike,
            "action": f"/admin/edit/{bike_id}",
            "brands": brands,
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.post("/edit/{bike_id}")
async def edit_bike(
    request: Request,
    bike_id: int,
    name: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    price: int = Form(...),
    mileage: int = Form(...),
    engine: int = Form(...),
    category: str = Form(...),
    color: str = Form(...),
    condition: str = Form(...),
    description: str = Form(""),
    youtube_url: str = Form(""),
    status: str = Form("available"),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    from src.repositories.bike_repo import BikeRepository

    bike = BikeRepository(db).get(bike_id)
    if not bike:
        raise HTTPException(404)
    BikeService(db).update(
        bike=bike,
        data={
            "name": name,
            "brand": brand,
            "model": model,
            "year": year,
            "price": price,
            "mileage": mileage,
            "engine": engine,
            "category": category,
            "color": color,
            "condition": condition,
            "description": description,
            "youtube_url": youtube_url,
            "available": status == "available",
            "status": status,
        },
        new_photo_files=photos or [],
    )
    return RedirectResponse("/admin", status_code=302)


@router.post("/delete/{bike_id}")
def delete_bike(
    request: Request,
    bike_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    from src.repositories.bike_repo import BikeRepository

    bike = BikeRepository(db).get(bike_id)
    if not bike:
        raise HTTPException(404)
    BikeService(db).delete(bike)
    return RedirectResponse("/admin", status_code=302)


@router.post("/photo/main/{photo_id}")
def set_main_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    bike_id = BikeService(db).set_main_photo(photo_id)
    if not bike_id:
        raise HTTPException(404)
    return RedirectResponse(f"/admin/edit/{bike_id}", status_code=302)


@router.post("/photo/delete/{photo_id}")
def delete_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    bike_id = BikeService(db).delete_photo(photo_id)
    if not bike_id:
        raise HTTPException(404)
    return RedirectResponse(f"/admin/edit/{bike_id}", status_code=302)
