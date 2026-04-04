from sqlalchemy import Column, Integer, String

from src.db.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    logo = Column(String(300), default="")
