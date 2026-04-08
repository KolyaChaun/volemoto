import random
from sqlalchemy.orm import Session

from src.db.database import SessionLocal


def _gen_article(db: Session) -> str:
    from src.models.bike import Bike
    while True:
        code = f"{random.randint(0, 999999):06d}"
        if not db.query(Bike).filter_by(article=code).first():
            return code


def fill_missing_articles() -> None:
    from src.models.bike import Bike
    db = SessionLocal()
    try:
        bikes = db.query(Bike).filter(
            (Bike.article == None) | (Bike.article == "")
        ).all()
        for bike in bikes:
            bike.article = _gen_article(db)
        if bikes:
            db.commit()
    finally:
        db.close()
