from sqlalchemy import Column, Integer, String
from src.db.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id            = Column(Integer, primary_key=True)
    username      = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)