import random
from sqlalchemy import text, inspect as sa_inspect
from sqlalchemy.orm import Session

from src.db.database import engine, SessionLocal


def _add_column_if_missing(table: str, column: str, definition: str) -> None:
    with engine.connect() as conn:
        cols = [c["name"] for c in sa_inspect(engine).get_columns(table)]
        if column not in cols:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
            conn.commit()


def run_migrations() -> None:
    _add_column_if_missing("brands",  "logo",    "VARCHAR(300) DEFAULT ''")
    _add_column_if_missing("reviews", "is_read", "BOOLEAN DEFAULT FALSE")
    _add_column_if_missing("bikes",   "article", "VARCHAR(10) DEFAULT ''")


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
