from sqlalchemy.orm import Session
from src.models.review import Review


def unread_count(db: Session) -> int:
    return db.query(Review).filter_by(is_read=False).count()
