from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.core.config import settings, templates
from src.core.security import (
    SESSION_COOKIE,
    SESSION_MAX_AGE,
    create_session_token,
    verify_password,
)
from src.db.database import get_db
from src.models.admin import Admin

router = APIRouter(tags=["Авторизація"])


@router.get("/admin/login")
def admin_login_page(request: Request):
    if request.cookies.get(SESSION_COOKIE):
        return RedirectResponse("/admin", status_code=302)
    return templates.TemplateResponse(request, "admin/login.html", {"error": None})


@router.post("/admin/login")
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter_by(username=username.strip()).first()
    if not admin or not verify_password(password, admin.password_hash):
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Невірний логін або пароль"},
            status_code=401,
        )
    token = create_session_token(admin.id)
    resp = RedirectResponse("/admin", status_code=302)
    resp.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )
    return resp


@router.post("/admin/logout")
def admin_logout():
    resp = RedirectResponse("/admin/login", status_code=302)
    resp.delete_cookie(SESSION_COOKIE)
    return resp
