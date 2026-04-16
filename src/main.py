from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.constants import OPENAPI_TAGS
from src.core.config import templates
from src.core.csrf import CSRFMiddleware
from src.routers import admin, auth, public, reviews
from src.services.currency_service import (
    get_cached_rate,
    init_from_db,
    refresh_rate,
    start_background_refresh,
    uah_price,
    usd_amount,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    templates.env.globals.update({"uah_price": uah_price, "usd_amount": usd_amount})
    init_from_db()
    if get_cached_rate() is None:
        refresh_rate()
    start_background_refresh()
    yield


app = FastAPI(
    title="VOLE MOTO",
    description="API мотосалону VOLE MOTO — мотоцикли, екіпіровка, запчастини.",
    version="1.0.0",
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
)

app.add_middleware(CSRFMiddleware)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/media", StaticFiles(directory="src/media"), name="media")

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(reviews.router)


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc):
    return RedirectResponse("/admin/login", status_code=302)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
