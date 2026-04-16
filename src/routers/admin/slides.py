from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.config import templates
from src.core.security import require_admin
from src.db.database import get_db
from src.models.admin import Admin
from src.models.hero_slide import HeroSlide
from src.repositories.review_repo import ReviewRepository
from src.services.file_service import delete_file_by_path, save_single_file
from src.services.settings_service import get_settings, set_setting

router = APIRouter(tags=["Адмін — слайди"])


@router.get("/hero", response_class=HTMLResponse)
def hero_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    slides = db.query(HeroSlide).order_by(HeroSlide.sort_order, HeroSlide.id).all()
    settings = get_settings(db)
    return templates.TemplateResponse(
        request,
        "admin/hero.html",
        {
            "slides": slides,
            "unread": ReviewRepository(db).unread_count(),
            "sold_count": settings.get("sold_count", "620"),
            "subscribers_count": settings.get("subscribers_count", "13 600"),
        },
    )


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


@router.post("/hero/settings")
def hero_settings_update(
    request: Request,
    sold_count: str = Form(...),
    subscribers_count: str = Form(...),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    set_setting(db, "sold_count", sold_count.strip())
    set_setting(db, "subscribers_count", subscribers_count.strip())
    db.commit()
    return RedirectResponse("/admin", status_code=302)


@router.post("/hero/delete/{slide_id}")
def hero_delete(
    request: Request,
    slide_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    slide = db.query(HeroSlide).filter_by(id=slide_id).first()
    if not slide:
        raise HTTPException(404)
    delete_file_by_path(slide.path)
    db.delete(slide)
    db.commit()
    return RedirectResponse("/admin/hero", status_code=302)
