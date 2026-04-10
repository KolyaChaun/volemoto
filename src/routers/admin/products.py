from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.constants import (
    GEAR_CATEGORIES,
    PARTS_CATEGORIES,
    PARTS_SUBCATS,
    PRODUCT_CATEGORIES,
)
from src.core.config import templates
from src.core.security import require_admin
from src.db.database import get_db
from src.models.admin import Admin
from src.models.brand import Brand
from src.repositories.product_repo import ProductRepository
from src.repositories.review_repo import ReviewRepository
from src.services.product_service import ProductService

router = APIRouter(tags=["Адмін — товари"])


@router.get("/products", response_class=HTMLResponse)
def products_list(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    products = ProductRepository(db).list_all()
    return templates.TemplateResponse(
        request,
        "admin/products.html",
        {
            "products": products,
            "total": len(products),
            "helmets": sum(1 for p in products if p.category == "helmets"),
            "gloves": sum(1 for p in products if p.category == "gloves"),
            "gear": sum(1 for p in products if p.category == "gear"),
            "parts": sum(1 for p in products if p.category in PARTS_CATEGORIES),
            "cats": PRODUCT_CATEGORIES,
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.get("/products/add", response_class=HTMLResponse)
def add_product_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    return templates.TemplateResponse(
        request,
        "admin/add_product.html",
        {
            "product": None,
            "action": "/admin/products/add",
            "brands": db.query(Brand).order_by(Brand.name).all(),
            "cats": PRODUCT_CATEGORIES,
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.post("/products/add")
async def add_product(
    request: Request,
    name: str = Form(...),
    brand: str = Form(""),
    category: str = Form(...),
    price: int = Form(...),
    condition: str = Form(...),
    size: str = Form(""),
    compatibility: str = Form(""),
    description: str = Form(""),
    youtube_url: str = Form(""),
    status: str = Form("available"),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    ProductService(db).create(
        data={
            "name": name,
            "brand": brand,
            "category": category,
            "price": price,
            "condition": condition,
            "size": size,
            "compatibility": compatibility,
            "description": description,
            "youtube_url": youtube_url,
            "available": status == "available",
            "status": status,
        },
        photo_files=photos or [],
    )
    return RedirectResponse("/admin/products", status_code=302)


@router.get("/products/edit/{product_id}", response_class=HTMLResponse)
def edit_product_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    return templates.TemplateResponse(
        request,
        "admin/add_product.html",
        {
            "product": product,
            "action": f"/admin/products/edit/{product_id}",
            "brands": db.query(Brand).order_by(Brand.name).all(),
            "cats": PRODUCT_CATEGORIES,
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.post("/products/edit/{product_id}")
async def edit_product(
    request: Request,
    product_id: int,
    name: str = Form(...),
    brand: str = Form(""),
    category: str = Form(...),
    price: int = Form(...),
    condition: str = Form(...),
    size: str = Form(""),
    compatibility: str = Form(""),
    description: str = Form(""),
    youtube_url: str = Form(""),
    status: str = Form("available"),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    ProductService(db).update(
        product=product,
        data={
            "name": name,
            "brand": brand,
            "category": category,
            "price": price,
            "condition": condition,
            "size": size,
            "compatibility": compatibility,
            "description": description,
            "youtube_url": youtube_url,
            "available": status == "available",
            "status": status,
        },
        new_photo_files=photos or [],
    )
    return RedirectResponse("/admin/products", status_code=302)


@router.post("/products/delete/{product_id}")
def delete_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    ProductService(db).delete(product)
    return RedirectResponse("/admin/products", status_code=302)


@router.post("/products/photo/main/{photo_id}")
def set_product_main_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product_id = ProductService(db).set_main_photo(photo_id)
    if not product_id:
        raise HTTPException(404)
    return RedirectResponse(f"/admin/products/edit/{product_id}", status_code=302)


@router.post("/products/photo/delete/{photo_id}")
def delete_product_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product_id = ProductService(db).delete_photo(photo_id)
    if not product_id:
        raise HTTPException(404)
    return RedirectResponse(f"/admin/products/edit/{product_id}", status_code=302)


@router.get("/gear", response_class=HTMLResponse)
def gear_list(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    from src.models.product import Product

    products = (
        db.query(Product)
        .filter(Product.category.in_(GEAR_CATEGORIES))
        .order_by(Product.id.desc())
        .all()
    )
    return templates.TemplateResponse(
        request,
        "admin/gear_list.html",
        {
            "products": products,
            "total": len(products),
            "helmets": sum(1 for p in products if p.category == "helmets"),
            "gloves": sum(1 for p in products if p.category == "gloves"),
            "gear": sum(1 for p in products if p.category == "gear"),
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.get("/gear/add", response_class=HTMLResponse)
def add_gear_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    return templates.TemplateResponse(
        request,
        "admin/add_gear.html",
        {
            "product": None,
            "action": "/admin/gear/add",
            "brands": db.query(Brand).order_by(Brand.name).all(),
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.post("/gear/add")
async def add_gear(
    request: Request,
    name: str = Form(...),
    brand: str = Form(""),
    category: str = Form(...),
    price: int = Form(...),
    condition: str = Form(""),
    size_list: List[str] = Form(default=[]),
    color_list: List[str] = Form(default=[]),
    model: str = Form(""),
    description: str = Form(""),
    status: str = Form("available"),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    ProductService(db).create(
        data={
            "name": name,
            "brand": brand,
            "category": category,
            "price": price,
            "condition": condition,
            "size": ",".join(size_list),
            "color": ",".join(color_list),
            "model": model,
            "description": description,
            "available": status == "available",
            "status": status,
        },
        photo_files=photos or [],
    )
    return RedirectResponse("/admin/gear", status_code=302)


@router.get("/gear/edit/{product_id}", response_class=HTMLResponse)
def edit_gear_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    return templates.TemplateResponse(
        request,
        "admin/add_gear.html",
        {
            "product": product,
            "action": f"/admin/gear/edit/{product_id}",
            "brands": db.query(Brand).order_by(Brand.name).all(),
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.post("/gear/edit/{product_id}")
async def edit_gear(
    request: Request,
    product_id: int,
    name: str = Form(...),
    brand: str = Form(""),
    category: str = Form(...),
    price: int = Form(...),
    condition: str = Form(""),
    size_list: List[str] = Form(default=[]),
    color_list: List[str] = Form(default=[]),
    model: str = Form(""),
    description: str = Form(""),
    status: str = Form("available"),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    ProductService(db).update(
        product=product,
        data={
            "name": name,
            "brand": brand,
            "category": category,
            "price": price,
            "condition": condition,
            "size": ",".join(size_list),
            "color": ",".join(color_list),
            "model": model,
            "description": description,
            "available": status == "available",
            "status": status,
        },
        new_photo_files=photos or [],
    )
    return RedirectResponse("/admin/gear", status_code=302)


@router.post("/gear/delete/{product_id}")
def delete_gear(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    ProductService(db).delete(product)
    return RedirectResponse("/admin/gear", status_code=302)


@router.post("/gear/photo/main/{photo_id}")
def gear_main_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product_id = ProductService(db).set_main_photo(photo_id)
    if not product_id:
        raise HTTPException(404)
    return RedirectResponse(f"/admin/gear/edit/{product_id}", status_code=302)


@router.post("/gear/photo/delete/{photo_id}")
def delete_gear_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product_id = ProductService(db).delete_photo(photo_id)
    if not product_id:
        raise HTTPException(404)
    return RedirectResponse(f"/admin/gear/edit/{product_id}", status_code=302)


@router.get("/parts", response_class=HTMLResponse)
def parts_list(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    from src.models.product import Product

    products = (
        db.query(Product)
        .filter(Product.category.in_(PARTS_CATEGORIES))
        .order_by(Product.id.desc())
        .all()
    )
    return templates.TemplateResponse(
        request,
        "admin/parts_list.html",
        {
            "products": products,
            "total": len(products),
            "parts_new": sum(1 for p in products if p.category == "parts_new"),
            "parts_used": sum(1 for p in products if p.category == "parts_used"),
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.get("/parts/add", response_class=HTMLResponse)
def add_parts_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    return templates.TemplateResponse(
        request,
        "admin/add_parts.html",
        {
            "product": None,
            "action": "/admin/parts/add",
            "brands": db.query(Brand).order_by(Brand.name).all(),
            "parts_subcats": PARTS_SUBCATS,
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.post("/parts/add")
async def add_parts(
    request: Request,
    name: str = Form(...),
    brand: str = Form(""),
    color: str = Form(""),
    category: str = Form(...),
    subcategory: str = Form(""),
    model: str = Form(""),
    compatibility: str = Form(""),
    price: int = Form(...),
    condition: str = Form(""),
    description: str = Form(""),
    status: str = Form("available"),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    ProductService(db).create(
        data={
            "name": name,
            "brand": brand,
            "color": color,
            "category": category,
            "subcategory": subcategory,
            "model": model,
            "compatibility": compatibility,
            "price": price,
            "condition": condition,
            "description": description,
            "available": status == "available",
            "status": status,
        },
        photo_files=photos or [],
    )
    return RedirectResponse("/admin/parts", status_code=302)


@router.get("/parts/edit/{product_id}", response_class=HTMLResponse)
def edit_parts_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    return templates.TemplateResponse(
        request,
        "admin/add_parts.html",
        {
            "product": product,
            "action": f"/admin/parts/edit/{product_id}",
            "brands": db.query(Brand).order_by(Brand.name).all(),
            "parts_subcats": PARTS_SUBCATS,
            "unread": ReviewRepository(db).unread_count(),
        },
    )


@router.post("/parts/edit/{product_id}")
async def edit_parts(
    request: Request,
    product_id: int,
    name: str = Form(...),
    brand: str = Form(""),
    color: str = Form(""),
    category: str = Form(...),
    subcategory: str = Form(""),
    model: str = Form(""),
    compatibility: str = Form(""),
    price: int = Form(...),
    condition: str = Form(""),
    description: str = Form(""),
    status: str = Form("available"),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    ProductService(db).update(
        product=product,
        data={
            "name": name,
            "brand": brand,
            "color": color,
            "category": category,
            "subcategory": subcategory,
            "model": model,
            "compatibility": compatibility,
            "price": price,
            "condition": condition,
            "description": description,
            "available": status == "available",
            "status": status,
        },
        new_photo_files=photos or [],
    )
    return RedirectResponse("/admin/parts", status_code=302)


@router.post("/parts/delete/{product_id}")
def delete_parts(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(404)
    ProductService(db).delete(product)
    return RedirectResponse("/admin/parts", status_code=302)


@router.post("/parts/photo/main/{photo_id}")
def parts_main_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product_id = ProductService(db).set_main_photo(photo_id)
    if not product_id:
        raise HTTPException(404)
    return RedirectResponse(f"/admin/parts/edit/{product_id}", status_code=302)


@router.post("/parts/photo/delete/{photo_id}")
def delete_parts_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    product_id = ProductService(db).delete_photo(photo_id)
    if not product_id:
        raise HTTPException(404)
    return RedirectResponse(f"/admin/parts/edit/{product_id}", status_code=302)
