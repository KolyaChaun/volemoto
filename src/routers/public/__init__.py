from fastapi import APIRouter

from src.routers.public import bikes, pages, products, search

router = APIRouter()
router.include_router(pages.router)
router.include_router(bikes.router)
router.include_router(products.router)
router.include_router(search.router)
