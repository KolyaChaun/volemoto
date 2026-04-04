import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from src.db.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    rating     = Column(Integer, nullable=False)
    text       = Column(Text, nullable=False)
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    replies = relationship("ReviewReply", back_populates="review",
                           cascade="all, delete-orphan", order_by="ReviewReply.id")


class ReviewReply(Base):
    __tablename__ = "review_replies"

    id         = Column(Integer, primary_key=True, index=True)
    review_id  = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    name       = Column(String(100), nullable=False)
    text       = Column(Text, nullable=False)
    is_admin   = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    review = relationship("Review", back_populates="replies")
