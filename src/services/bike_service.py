import random
from sqlalchemy.orm import Session
from src.models.bike import Bike


def gen_article(db: Session) -> str:
    while True:
        code = f"{random.randint(0, 999999):06d}"
        if not db.query(Bike).filter_by(article=code).first():
            return code
