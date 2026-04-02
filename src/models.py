from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Bike(Base):
    __tablename__ = "bikes"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(200))
    brand       = Column(String(100))
    model       = Column(String(100))
    year        = Column(Integer)
    price       = Column(Integer)
    mileage     = Column(Integer)
    engine      = Column(Integer)
    category    = Column(String(20))
    color       = Column(String(100))
    condition   = Column(String(100))
    description = Column(Text, default="")
    photo       = Column(String(300), default="")  # головне фото (перше)
    available   = Column(Boolean, default=True)

    photos      = relationship("BikePhoto", back_populates="bike",
                               cascade="all, delete-orphan", order_by="BikePhoto.id")


class Brand(Base):
    __tablename__ = "brands"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    logo = Column(String(300), default="")  # шлях до логотипу


class BikePhoto(Base):
    __tablename__ = "bike_photos"

    id      = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"), nullable=False)
    path    = Column(String(300), nullable=False)

    bike    = relationship("Bike", back_populates="photos")