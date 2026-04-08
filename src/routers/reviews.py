from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from src.core.config import templates
from src.core.security import require_admin, get_optional_admin
from src.db.database import get_db
from src.models.admin import Admin
from src.models.review import Review, ReviewReply, ReviewPhoto
from src.services.file_service import save_photos

router = APIRouter()


# ── PUBLIC ────────────────────────────────────────────

@router.get("/reviews", response_class=HTMLResponse)
def reviews_page(
    request: Request,
    sort: str = "new",
    limit: int = 20,
    db: Session = Depends(get_db),
    is_admin: bool = Depends(get_optional_admin),
):
    q = db.query(Review)
    if sort == "rating":
        q = q.order_by(Review.rating.desc())
    elif sort == "old":
        q = q.order_by(Review.id.asc())
    else:
        q = q.order_by(Review.id.desc())
    all_reviews = q.all()
    total       = len(all_reviews)
    avg         = round(sum(r.rating for r in all_reviews) / total, 1) if total else 0
    counts      = {i: sum(1 for r in all_reviews if r.rating == i) for i in range(1, 6)}
    return templates.TemplateResponse(request, "pages/reviews.html", {
        "reviews":  all_reviews[:limit],
        "total":    total,
        "avg":      avg,
        "counts":   counts,
        "sort":     sort,
        "is_admin": is_admin,
        "limit":    limit,
        "has_more": total > limit,
    })


@router.post("/reviews")
async def reviews_add(
    request: Request,
    name:   str = Form(...),
    rating: int = Form(...),
    text:   str = Form(...),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if 1 <= rating <= 5 and name.strip() and text.strip():
        review = Review(name=name.strip(), rating=rating, text=text.strip())
        db.add(review)
        db.flush()
        if photos:
            paths = save_photos([f for f in photos if f and f.filename], "reviews")
            for path in paths:
                db.add(ReviewPhoto(review_id=review.id, path=path))
        db.commit()
    return RedirectResponse("/reviews", status_code=302)


@router.post("/reviews/{review_id}/reply")
def review_user_reply(
    request: Request,
    review_id: int,
    name: str = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter_by(id=review_id).first()
    if review and name.strip() and text.strip():
        db.add(ReviewReply(review_id=review_id, name=name.strip(), text=text.strip(), is_admin=False))
        db.commit()
    return RedirectResponse("/reviews", status_code=302)


# ── ADMIN ─────────────────────────────────────────────

@router.get("/admin/reviews", response_class=HTMLResponse)
def admin_reviews(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    reviews = db.query(Review).order_by(Review.id.desc()).all()
    db.query(Review).filter_by(is_read=False).update({"is_read": True})
    db.commit()
    return templates.TemplateResponse(request, "admin/reviews.html", {
        "reviews": reviews, "unread": 0,
    })


@router.post("/admin/reviews/{review_id}/reply")
def admin_review_reply(
    request: Request,
    review_id: int,
    text: str = Form(...),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    if text.strip():
        db.add(ReviewReply(review_id=review_id, name="VOLE MOTO", text=text.strip(), is_admin=True))
        db.commit()
    return RedirectResponse("/admin/reviews", status_code=302)


@router.post("/admin/reviews/{review_id}/delete")
def admin_review_delete(
    request: Request, review_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    review = db.query(Review).filter_by(id=review_id).first()
    if review:
        db.delete(review)
        db.commit()
    return RedirectResponse("/admin/reviews", status_code=302)


@router.post("/admin/reviews/reply/{reply_id}/delete")
def admin_reply_delete(
    request: Request, reply_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    reply = db.query(ReviewReply).filter_by(id=reply_id).first()
    if reply:
        db.delete(reply)
        db.commit()
    return RedirectResponse("/admin/reviews", status_code=302)