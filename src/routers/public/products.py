from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.constants import (
    BIKE_CONDITIONS,
    GEAR_CATEGORIES,
    PARTS_CATEGORIES,
    PARTS_SUBCATS,
    PRODUCT_CATEGORIES,
    PRODUCT_CONDITIONS,
)
from src.core.config import templates
from src.db.database import get_db
from src.models.product import Product
from src.repositories.product_repo import (
    EquipmentFilters,
    PartsFilters,
    ProductRepository,
)

router = APIRouter(tags=["Сайт — товари"])


def _to_int(v: Optional[str]) -> Optional[int]:
    return int(v) if v and v.strip() else None


def _flag(v: Optional[str]) -> bool:
    return v in ("true", "on", "1", True)


@router.get("/equipment", response_class=HTMLResponse)
def equipment_page(
    request: Request,
    db: Session = Depends(get_db),
    cat: Optional[str] = None,
    sort: str = "newest",
    brand: List[str] = Query(default=[]),
    color: List[str] = Query(default=[]),
    size: List[str] = Query(default=[]),
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    condition: Optional[str] = None,
    available_only: Optional[str] = None,
):
    filters = EquipmentFilters(
        cat=cat if cat in GEAR_CATEGORIES else None,
        brands=[b.strip() for b in brand if b and b.strip()],
        colors=[c.strip() for c in color if c and c.strip()],
        sizes=[s.strip() for s in size if s and s.strip()],
        min_price=_to_int(min_price),
        max_price=_to_int(max_price),
        condition=condition.strip() if condition and condition.strip() else None,
        available_only=_flag(available_only),
        sort=sort,
    )
    repo = ProductRepository(db)
    items, all_items = repo.get_equipment(GEAR_CATEGORIES, filters)
    facets = repo.equipment_facets(all_items)

    return templates.TemplateResponse(
        request,
        "pages/equipment.html",
        {
            "items": items,
            "total": len(items),
            "cat": filters.cat,
            "cats": {
                k: v for k, v in PRODUCT_CATEGORIES.items() if k in GEAR_CATEGORIES
            },
            "sort": sort,
            "selected_brands": filters.brands,
            "condition": filters.condition,
            "selected_colors": filters.colors,
            "selected_sizes": filters.sizes,
            "available_only": filters.available_only,
            "min_price": filters.min_price,
            "max_price": filters.max_price,
            "conditions": PRODUCT_CONDITIONS,
            **facets,
        },
    )


@router.get("/parts", response_class=HTMLResponse)
def parts_page(
    request: Request,
    db: Session = Depends(get_db),
    cat: Optional[str] = None,
    sort: str = "newest",
    brand: List[str] = Query(default=[]),
    subcategory: Optional[str] = None,
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    condition: Optional[str] = None,
    available_only: Optional[str] = None,
):
    all_subcat_keys = {g["key"] for g in PARTS_SUBCATS}
    subcat_v = subcategory.strip() if subcategory and subcategory.strip() else None
    if subcat_v:
        base_key = subcat_v.split("::")[0]
        if base_key not in all_subcat_keys:
            subcat_v = None

    filters = PartsFilters(
        cat=cat if cat in PARTS_CATEGORIES else None,
        brands=[b.strip() for b in brand if b and b.strip()],
        subcategory=subcat_v,
        min_price=_to_int(min_price),
        max_price=_to_int(max_price),
        condition=condition.strip() if condition and condition.strip() else None,
        available_only=_flag(available_only),
        sort=sort,
    )
    repo = ProductRepository(db)
    items = repo.get_parts(PARTS_CATEGORIES, filters)
    all_brands, brand_counts = repo.parts_brands(PARTS_CATEGORIES)
    # used_subcats = repo.parts_used_subcats(PARTS_CATEGORIES)

    all_parts_flat = repo.get_parts(PARTS_CATEGORIES, PartsFilters())
    all_subcats_in_db = {p.subcategory for p in all_parts_flat if p.subcategory}
    used_subcats = {s.split("::")[0] for s in all_subcats_in_db}

    return templates.TemplateResponse(
        request,
        "pages/parts.html",
        {
            "items": items,
            "total": len(items),
            "cat": filters.cat,
            "cats": {
                k: v for k, v in PRODUCT_CATEGORIES.items() if k in PARTS_CATEGORIES
            },
            "sort": sort,
            "selected_brands": filters.brands,
            "condition": filters.condition,
            "available_only": filters.available_only,
            "subcategory": filters.subcategory,
            "min_price": filters.min_price,
            "max_price": filters.max_price,
            "brands": all_brands,
            "brand_counts": brand_counts,
            "parts_subcats": [
                {**g, "sub": [s for s in g["sub"] if g["key"] + "::" + s in all_subcats_in_db]}
                for g in PARTS_SUBCATS if g["key"] in used_subcats
            ],
            "conditions": BIKE_CONDITIONS,
        },
    )


@router.get("/equipment/{slug}", response_class=HTMLResponse)
@router.get("/parts/{slug}", response_class=HTMLResponse)
def product_detail(request: Request, slug: str, db: Session = Depends(get_db)):
    try:
        product_id = int(slug.rsplit("_", 1)[-1])
    except (ValueError, IndexError):
        raise HTTPException(status_code=404)
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(status_code=404)
    if product.subcategory:
        similar = (
            db.query(Product)
            .filter(
                Product.subcategory == product.subcategory, Product.id != product.id
            )
            .limit(3)
            .all()
        )
    else:
        similar = (
            db.query(Product)
            .filter(Product.category == product.category, Product.id != product.id)
            .limit(3)
            .all()
        )
    return templates.TemplateResponse(
        request,
        "pages/parts_detail.html",
        {"product": product, "similar": similar},
    )
