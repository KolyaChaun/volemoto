from typing import List

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core.config import templates
from src.core.rate_limit import rate_limit
from src.core.security import get_optional_admin
from src.db.database import get_db
from src.models.review import Review, ReviewReply
from src.repositories.review_repo import ReviewRepository
from src.services.file_service import InvalidFileError, save_photos

router = APIRouter(tags=["Відгуки"])


@router.get("/reviews", response_class=HTMLResponse)
def reviews_page(
    request: Request,
    sort: str = "new",
    limit: int = 20,
    db: Session = Depends(get_db),
    is_admin: bool = Depends(get_optional_admin),
):
    all_reviews = ReviewRepository(db).list_all(sort)
    total = len(all_reviews)
    avg = round(sum(r.rating for r in all_reviews) / total, 1) if total else 0
    counts = {i: sum(1 for r in all_reviews if r.rating == i) for i in range(1, 6)}
    return templates.TemplateResponse(
        request,
        "pages/reviews.html",
        {
            "reviews": all_reviews[:limit],
            "total": total,
            "avg": avg,
            "counts": counts,
            "sort": sort,
            "is_admin": is_admin,
            "limit": limit,
            "has_more": total > limit,
        },
    )


@router.post("/reviews")
@rate_limit(max_calls=5, period=60)
async def reviews_add(
    request: Request,
    name: str = Form(...),
    rating: int = Form(...),
    text: str = Form(...),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    MAX_PHOTOS = 5
    if not (1 <= rating <= 5 and name.strip() and text.strip()):
        return RedirectResponse("/reviews", status_code=302)
    valid_photos = [f for f in (photos or []) if f and f.filename][:MAX_PHOTOS]
    try:
        photo_paths = save_photos(valid_photos, "reviews")
    except InvalidFileError:
        return RedirectResponse("/reviews", status_code=302)
    ReviewRepository(db).save(
        Review(name=name.strip(), rating=rating, text=text.strip()),
        photo_paths,
    )
    return RedirectResponse("/reviews", status_code=302)


@router.post("/reviews/{review_id}/reply")
@rate_limit(max_calls=5, period=60)
def review_user_reply(
    request: Request,
    review_id: int,
    name: str = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db),
):
    repo = ReviewRepository(db)
    review = repo.get(review_id)
    if review and name.strip() and text.strip():
        repo.add_reply(
            ReviewReply(
                review_id=review_id,
                name=name.strip(),
                text=text.strip(),
                is_admin=False,
            )
        )
    return RedirectResponse("/reviews", status_code=302)
