import re

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.db.database import Base


def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[\s]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    article = Column(String(10), default="")
    name = Column(String(200))
    brand = Column(String(100), default="")
    price = Column(Integer, default=0)
    condition = Column(String(100), default="")
    available = Column(Boolean, default=True)
    status = Column(String(30), default="available")
    description = Column(Text, default="")
    photo = Column(String(300), default="")
    category = Column(String(30))
    size = Column(String(100), default="")
    compatibility = Column(
        String(500), default=""
    )
    model = Column(String(200), default="")
    color = Column(String(100), default="")
    subcategory = Column(String(100), default="")
    youtube_url = Column(String(500), default="")

    photos = relationship(
        "ProductPhoto",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductPhoto.id",
    )

    @property
    def slug(self) -> str:
        return f"{_slugify(self.name or '')}_{self.id}"


class ProductPhoto(Base):
    __tablename__ = "product_photos"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    path = Column(String(300), nullable=False)

    product = relationship("Product", back_populates="photos")
