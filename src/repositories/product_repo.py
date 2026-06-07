from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.product import Product, ProductPhoto


def _split_vals(s: Optional[str]) -> list[str]:
    return [x.strip() for x in (s or "").split(",") if x.strip()]


@dataclass
class EquipmentFilters:
    cat: Optional[str] = None
    brands: list[str] = field(default_factory=list)
    colors: list[str] = field(default_factory=list)
    sizes: list[str] = field(default_factory=list)
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    condition: Optional[str] = None
    available_only: bool = False
    sort: str = "newest"


@dataclass
class PartsFilters:
    cat: Optional[str] = None
    brands: list[str] = field(default_factory=list)
    subcategory: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    condition: Optional[str] = None
    available_only: bool = False
    sort: str = "newest"


_SORT_MAP = {
    "price_asc": Product.price.asc(),
    "price_desc": Product.price.desc(),
}


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def list_all(self) -> list[Product]:
        return self.db.query(Product).order_by(Product.id.desc()).all()

    def article_exists(self, article: str) -> bool:
        return self.db.query(Product).filter_by(article=article).first() is not None

    def get_equipment(
        self, categories: set[str], filters: EquipmentFilters
    ) -> tuple[list[Product], list[Product]]:
        """Returns (filtered_items, all_items_in_category)."""
        base_q = self.db.query(Product).filter(Product.category.in_(list(categories)))
        if filters.cat:
            base_q = base_q.filter(Product.category == filters.cat)
        all_items = base_q.all()

        q = base_q
        if filters.brands:
            q = q.filter(func.trim(Product.brand).in_(filters.brands))
        if filters.min_price:
            q = q.filter(Product.price >= filters.min_price)
        if filters.max_price:
            q = q.filter(Product.price <= filters.max_price)
        if filters.condition:
            q = q.filter(Product.condition == filters.condition)
        if filters.available_only:
            q = q.filter(Product.available == True)  # noqa: E712
        q = q.order_by(_SORT_MAP.get(filters.sort, Product.id.desc()))

        items = q.all()
        if filters.colors:
            items = [
                i
                for i in items
                if any(c in _split_vals(i.color) for c in filters.colors)
            ]
        if filters.sizes:
            items = [
                i for i in items if any(s in _split_vals(i.size) for s in filters.sizes)
            ]

        return items, all_items

    def equipment_facets(self, all_items: list[Product]) -> dict:
        brand_counts: dict[str, int] = {}
        color_counts: dict[str, int] = {}
        size_counts: dict[str, int] = {}
        for p in all_items:
            if p.brand:
                key = p.brand.strip()
                brand_counts[key] = brand_counts.get(key, 0) + 1
            for c in _split_vals(p.color):
                color_counts[c] = color_counts.get(c, 0) + 1
            for s in _split_vals(p.size):
                size_counts[s] = size_counts.get(s, 0) + 1
        return {
            "brands": sorted(brand_counts),
            "colors": sorted(color_counts),
            "sizes": sorted(size_counts),
            "brand_counts": brand_counts,
            "color_counts": color_counts,
            "size_counts": size_counts,
        }

    def get_parts(self, categories: set[str], filters: PartsFilters) -> list[Product]:
        q = self.db.query(Product).filter(Product.category.in_(list(categories)))
        if filters.cat:
            q = q.filter(Product.category == filters.cat)
        if filters.brands:
            q = q.filter(func.trim(Product.brand).in_(filters.brands))
        if filters.subcategory:
            q = q.filter(Product.subcategory.like(f"{filters.subcategory}%"))
        if filters.min_price:
            q = q.filter(Product.price >= filters.min_price)
        if filters.max_price:
            q = q.filter(Product.price <= filters.max_price)
        if filters.condition:
            q = q.filter(Product.condition == filters.condition)
        if filters.available_only:
            q = q.filter(Product.available == True)  # noqa: E712
        return q.order_by(_SORT_MAP.get(filters.sort, Product.id.desc())).all()

    def parts_brands(self, categories: set[str]) -> tuple[list[str], dict[str, int]]:
        """Returns (sorted_brands, brand_counts)."""
        products = (
            self.db.query(Product)
            .filter(Product.category.in_(list(categories)), Product.brand != "")
            .all()
        )
        counts: dict[str, int] = {}
        for p in products:
            counts[p.brand] = counts.get(p.brand, 0) + 1
        return sorted(counts), counts

    def parts_used_subcats(self, categories: set[str]) -> set[str]:
        result = set()
        for p in self.db.query(Product).filter(
                Product.category.in_(list(categories)),
                Product.subcategory != None,
                Product.subcategory != "",
        ).all():
            if p.subcategory:
                result.add(p.subcategory.split("::")[0])
        return result

    def save(self, product: Product, photo_paths: list[str] = ()) -> Product:
        self.db.add(product)
        self.db.flush()
        for path in photo_paths:
            self.db.add(ProductPhoto(product_id=product.id, path=path))
        self.db.commit()
        return product

    def add_photos(self, product_id: int, paths: list[str]) -> None:
        for path in paths:
            self.db.add(ProductPhoto(product_id=product_id, path=path))

    def photo_paths(self, product_id: int) -> list[str]:
        return [
            p.path
            for p in self.db.query(ProductPhoto).filter_by(product_id=product_id).all()
        ]

    def get_photo(self, photo_id: int) -> ProductPhoto | None:
        return self.db.get(ProductPhoto, photo_id)

    def delete_photo(self, photo: ProductPhoto) -> None:
        self.db.delete(photo)

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()
