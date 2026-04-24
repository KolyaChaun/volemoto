import re
from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from src.constants import GEAR_CATEGORIES
from src.core.config import settings
from src.db.database import get_db
from src.models.bike import Bike
from src.models.product import Product

router = APIRouter(tags=["SEO"])

_STATIC_URLS = [
    ("/",                       "1.0", "daily"),
    ("/catalog/moto",           "0.9", "weekly"),
    ("/catalog/moped",          "0.9", "weekly"),
    ("/catalog/quad",           "0.9", "weekly"),
    ("/equipment",              "0.8", "weekly"),
    ("/parts",                  "0.8", "weekly"),
    ("/brands",                 "0.5", "monthly"),
    ("/reviews",                "0.5", "monthly"),
    ("/contacts",               "0.4", "monthly"),
    ("/otrimannya-i-oplata",    "0.3", "monthly"),
    ("/povernennya-ta-obmin",   "0.3", "monthly"),
]


def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return re.sub(r"_+", "_", s).strip("_")


def _url_entry(loc: str, priority: str, changefreq: str, lastmod: str) -> str:
    return (
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        f"  </url>"
    )


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    return (
        f"User-agent: *\n"
        f"Allow: /\n"
        f"Disallow: /admin/\n"
        f"Sitemap: {settings.site_url}/sitemap.xml\n"
    )


@router.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)):
    base = settings.site_url.rstrip("/")
    today = date.today().isoformat()
    entries = []

    for path, priority, changefreq in _STATIC_URLS:
        entries.append(_url_entry(f"{base}{path}", priority, changefreq, today))

    bikes = db.query(Bike.id, Bike.brand, Bike.model, Bike.category).all()
    for b in bikes:
        slug = f"{_slugify(b.brand or '')}_{_slugify(b.model or '')}_{b.id}"
        entries.append(_url_entry(
            f"{base}/catalog/{b.category}/{slug}", "0.8", "weekly", today
        ))

    products = db.query(Product.id, Product.name, Product.category).all()
    for p in products:
        slug = f"{_slugify(p.name or '')}_{p.id}"
        prefix = "equipment" if p.category in GEAR_CATEGORIES else "parts"
        entries.append(_url_entry(
            f"{base}/{prefix}/{slug}", "0.8", "weekly", today
        ))

    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>"
    )
    return Response(content=body, media_type="application/xml")
