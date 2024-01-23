from fastapi import APIRouter
from src.dashbord.routers import filter_router
router = APIRouter()

router.include_router(
    filter_router.router,
    prefix=("/filters"),
    tags=["dashbord-filters"]
)

