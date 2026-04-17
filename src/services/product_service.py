from sqlalchemy.orm import Session

from src.models.product import Product
from src.repositories.product_repo import ProductRepository
from src.services.base_item_service import BaseItemService


class ProductService(BaseItemService[Product]):
    _owner_id_attr = "product_id"

    def _make_repo(self, db: Session) -> ProductRepository:
        return ProductRepository(db)

    def _make_model(self, article: str, photo: str, data: dict) -> Product:
        return Product(article=article, photo=photo, **data)
