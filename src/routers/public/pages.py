from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.constants import FALLBACK_SLIDES
from src.core.config import templates
from src.db.database import get_db
from src.models.bike import Bike
from src.models.brand import Brand
from src.models.hero_slide import HeroSlide
from src.models.review import Review
from src.services.settings_service import fmt_number, get_settings

router = APIRouter(tags=["Сайт — сторінки"])


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    motos = db.query(Bike).filter_by(category="moto").limit(6).all()
    mopeds = db.query(Bike).filter_by(category="moped").limit(6).all()
    quads = db.query(Bike).filter_by(category="quad").limit(6).all()
    slides = db.query(HeroSlide).order_by(HeroSlide.sort_order, HeroSlide.id).all()
    recent_reviews = db.query(Review).order_by(Review.id.desc()).limit(4).all()
    settings = get_settings(db)
    return templates.TemplateResponse(
        request,
        "pages/index.html",
        {
            "motos": motos,
            "mopeds": mopeds,
            "quads": quads,
            "slide_urls": [s.path for s in slides] if slides else FALLBACK_SLIDES,
            "recent_reviews": recent_reviews,
            "sold_count": settings.get("sold_count", "620"),
            "subscribers_count": fmt_number(settings.get("subscribers_count", "13600")),
        },
    )


@router.get("/brands", response_class=HTMLResponse)
def brands_page(request: Request, db: Session = Depends(get_db)):
    brands = db.query(Brand).order_by(Brand.name).all()
    return templates.TemplateResponse(request, "pages/brands.html", {"brands": brands})


@router.get("/contacts", response_class=HTMLResponse)
def contacts_page(request: Request):
    return templates.TemplateResponse(request, "pages/contacts.html", {})
