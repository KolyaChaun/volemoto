from sqlalchemy.orm import Session

from src.models.review import Review, ReviewPhoto, ReviewReply


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def unread_count(self) -> int:
        return self.db.query(Review).filter_by(is_read=False).count()

    def list_all(self, sort: str = "new") -> list[Review]:
        q = self.db.query(Review)
        if sort == "rating":
            q = q.order_by(Review.rating.desc())
        elif sort == "old":
            q = q.order_by(Review.id.asc())
        else:
            q = q.order_by(Review.id.desc())
        return q.all()

    def get(self, review_id: int) -> Review | None:
        return self.db.get(Review, review_id)

    def save(self, review: Review, photo_paths: list[str] = ()) -> Review:
        self.db.add(review)
        self.db.flush()
        for path in photo_paths:
            self.db.add(ReviewPhoto(review_id=review.id, path=path))
        self.db.commit()
        return review

    def add_reply(self, reply: ReviewReply) -> None:
        self.db.add(reply)
        self.db.commit()

    def mark_all_read(self) -> None:
        self.db.query(Review).filter_by(is_read=False).update({"is_read": True})
        self.db.commit()

    def delete(self, review: Review) -> None:
        self.db.delete(review)
        self.db.commit()

    def get_reply(self, reply_id: int) -> ReviewReply | None:
        return self.db.get(ReviewReply, reply_id)

    def delete_reply(self, reply: ReviewReply) -> None:
        self.db.delete(reply)
        self.db.commit()
