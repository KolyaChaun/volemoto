import random

from sqlalchemy.orm import Session

from src.models.product import Product
from src.repositories.product_repo import ProductRepository
from src.services.file_service import delete_file_by_path, save_photos


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def gen_article(self) -> str:
        while True:
            code = f"{random.randint(0, 999999):06d}"
            if not self.repo.article_exists(code):
                return code

    def create(self, data: dict, photo_files: list) -> Product:
        photo_paths = save_photos(photo_files, data["category"])
        product = Product(
            article=self.gen_article(),
            photo=photo_paths[0] if photo_paths else "",
            **data,
        )
        return self.repo.save(product, photo_paths)

    def update(self, product: Product, data: dict, new_photo_files: list) -> Product:
        new_paths = save_photos(new_photo_files, data.get("category", product.category))
        self.repo.add_photos(product.id, new_paths)
        for key, value in data.items():
            setattr(product, key, value)
        self.repo.flush()
        all_paths = self.repo.photo_paths(product.id)
        if not product.photo or product.photo not in all_paths:
            product.photo = all_paths[0] if all_paths else ""
        self.repo.commit()
        return product

    def delete(self, product: Product) -> None:
        for photo in product.photos:
            delete_file_by_path(photo.path)
        self.repo.delete(product)

    def set_main_photo(self, photo_id: int) -> int | None:
        photo = self.repo.get_photo(photo_id)
        if not photo:
            return None
        product = self.repo.get(photo.product_id)
        product.photo = photo.path
        self.repo.commit()
        return photo.product_id

    def delete_photo(self, photo_id: int) -> int | None:
        photo = self.repo.get_photo(photo_id)
        if not photo:
            return None
        product_id = photo.product_id
        delete_file_by_path(photo.path)
        self.repo.delete_photo(photo)
        self.repo.flush()
        product = self.repo.get(product_id)
        all_paths = self.repo.photo_paths(product_id)
        if not product.photo or product.photo not in all_paths:
            product.photo = all_paths[0] if all_paths else ""
        self.repo.commit()
        return product_id
