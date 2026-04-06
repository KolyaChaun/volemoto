from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.db.database import Base, engine
from src.db.init_db import run_migrations, fill_missing_articles
from src.routers import auth, public, admin, reviews

# ── DB SETUP ─────────────────────────────────────────
Base.metadata.create_all(bind=engine)
run_migrations()
fill_missing_articles()

# ── APP ──────────────────────────────────────────────
app = FastAPI(title="VOLE MOTO")

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/media",  StaticFiles(directory="src/media"),  name="media")

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(reviews.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
