from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.config import templates
from src.core.security import require_admin
from src.db.database import get_db
from src.models.admin import Admin
from src.models.brand import Brand
from src.repositories.review_repo import ReviewRepository
from src.services.file_service import delete_file_by_path, save_single_file

router = APIRouter(tags=["Адмін — бренди"])


@router.get("/brands", response_class=HTMLResponse)
def brands_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(
        request,
        "admin/add_brands.html",
        {"brands": brands, "unread": ReviewRepository(db).unread_count()},
    )


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
    logo_path = save_single_file(logo, "brands") if logo and logo.filename else ""
    db.add(Brand(name=name, logo=logo_path))
    db.commit()
    return RedirectResponse("/admin/brands", status_code=302)


@router.post("/brands/delete/{brand_id}")
def delete_brand(
    request: Request,
    brand_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    brand = db.query(Brand).filter_by(id=brand_id).first()
    if not brand:
        raise HTTPException(404)
    delete_file_by_path(brand.logo)
    db.delete(brand)
    db.commit()
    return RedirectResponse("/admin/brands", status_code=302)
