from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.db.init_db import fill_missing_articles
from src.routers import auth, public, admin, reviews

# ── APP ──────────────────────────────────────────────
app = FastAPI(title="VOLE MOTO")

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/media",  StaticFiles(directory="src/media"),  name="media")

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(reviews.router)


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc):
    """Любой 401 из require_admin → редирект на страницу входа."""
    return RedirectResponse("/admin/login", status_code=302)


# ── DB SETUP ─────────────────────────────────────────
# Миграции управляются через Alembic: `alembic upgrade head`
fill_missing_articles()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
