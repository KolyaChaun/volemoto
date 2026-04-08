import re
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from urllib.parse import urlparse, parse_qs
from sqlalchemy.orm import relationship

from src.db.database import Base


def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r'[\s]+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s


class Bike(Base):
    __tablename__ = "bikes"

    id          = Column(Integer, primary_key=True, index=True)
    article     = Column(String(10), default="")
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
    description  = Column(Text, default="")
    photo        = Column(String(300), default="")
    available    = Column(Boolean, default=True)
    status       = Column(String(30), default="available")
    youtube_url  = Column(String(500), default="")

    photos = relationship("BikePhoto", back_populates="bike",
                          cascade="all, delete-orphan", order_by="BikePhoto.id")

    @property
    def youtube_video_id(self) -> str:
        url = (self.youtube_url or "").strip()
        if not url:
            return ""
        parsed = urlparse(url)
        if parsed.hostname in ("youtu.be",):
            return parsed.path.lstrip("/")
        return parse_qs(parsed.query).get("v", [""])[0]

    @property
    def youtube_embed_url(self) -> str:
        vid = self.youtube_video_id
        return f"https://www.youtube.com/embed/{vid}" if vid else ""

    @property
    def slug(self) -> str:
        brand = _slugify(self.brand or "")
        model = _slugify(self.model or "")
        return f"{brand}_{model}_{self.id}"


class BikePhoto(Base):
    __tablename__ = "bike_photos"

    id      = Column(Integer, primary_key=True, index=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"), nullable=False)
    path    = Column(String(300), nullable=False)

    bike = relationship("Bike", back_populates="photos")
