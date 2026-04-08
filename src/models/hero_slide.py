from sqlalchemy import Column, Integer, String
from src.db.database import Base


class HeroSlide(Base):
    __tablename__ = "hero_slides"

    id         = Column(Integer, primary_key=True, index=True)
    path       = Column(String(300), nullable=False)
    sort_order = Column(Integer, default=0)
