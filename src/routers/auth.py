from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from src.core.config import templates, ADMIN_LOGIN, ADMIN_PASS

router = APIRouter()


@router.get("/admin/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse(request, "admin/login.html", {"error": None})


@router.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_LOGIN and password == ADMIN_PASS:
        resp = RedirectResponse("/admin", status_code=302)
        resp.set_cookie("admin", "ok", httponly=True)
        return resp
    return templates.TemplateResponse(request, "admin/login.html", {
        "error": "Невірний логін або пароль"
    })


@router.get("/admin/logout")
def admin_logout():
    resp = RedirectResponse("/admin/login", status_code=302)
    resp.delete_cookie("admin")
    return resp
