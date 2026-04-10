from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.config import templates
from src.core.security import require_admin
from src.db.database import get_db
from src.models.admin import Admin
from src.models.hero_slide import HeroSlide
from src.repositories.review_repo import ReviewRepository
from src.services.file_service import delete_file_by_path, save_single_file

router = APIRouter(tags=["Адмін — слайди"])


@router.get("/hero", response_class=HTMLResponse)
def hero_page(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    slides = db.query(HeroSlide).order_by(HeroSlide.sort_order, HeroSlide.id).all()
    return templates.TemplateResponse(
        request,
        "admin/hero.html",
        {"slides": slides, "unread": ReviewRepository(db).unread_count()},
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
