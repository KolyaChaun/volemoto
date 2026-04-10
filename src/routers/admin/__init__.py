from fastapi import APIRouter

from src.routers.admin import bikes, brands, products, reviews, slides

router = APIRouter(prefix="/admin")
router.include_router(bikes.router)
router.include_router(products.router)
router.include_router(reviews.router)
router.include_router(brands.router)
router.include_router(slides.router)
