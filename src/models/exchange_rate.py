from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from src.db.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True)
    currency = Column(String(10), unique=True, nullable=False)
    rate = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
