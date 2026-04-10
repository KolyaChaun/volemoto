from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.config import templates
from src.core.security import require_admin
from src.db.database import get_db
from src.models.admin import Admin
from src.models.review import ReviewReply
from src.repositories.review_repo import ReviewRepository

router = APIRouter(tags=["Адмін — відгуки"])


@router.get("/reviews", response_class=HTMLResponse)
def admin_reviews(
    request: Request,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    repo = ReviewRepository(db)
    reviews = repo.list_all()
    repo.mark_all_read()
    return templates.TemplateResponse(
        request,
        "admin/reviews.html",
        {"reviews": reviews, "unread": 0},
    )


@router.post("/reviews/{review_id}/reply")
def admin_review_reply(
    request: Request,
    review_id: int,
    text: str = Form(...),
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    if text.strip():
        ReviewRepository(db).add_reply(
            ReviewReply(
                review_id=review_id, name="VOLE MOTO", text=text.strip(), is_admin=True
            )
        )
    return RedirectResponse("/admin/reviews", status_code=302)


@router.post("/reviews/{review_id}/delete")
def admin_review_delete(
    request: Request,
    review_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    repo = ReviewRepository(db)
    review = repo.get(review_id)
    if not review:
        raise HTTPException(404)
    repo.delete(review)
    return RedirectResponse("/admin/reviews", status_code=302)


@router.post("/reviews/reply/{reply_id}/delete")
def admin_reply_delete(
    request: Request,
    reply_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(require_admin),
):
    repo = ReviewRepository(db)
    reply = repo.get_reply(reply_id)
    if not reply:
        raise HTTPException(404)
    repo.delete_reply(reply)
    return RedirectResponse("/admin/reviews", status_code=302)
