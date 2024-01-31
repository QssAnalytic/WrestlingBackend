from fastapi import APIRouter
from src.dashbord.routers import filter_routers, medal_routers
router = APIRouter()

router.include_router(
    filter_routers.router,
    prefix=("/filters"),
    tags=["dashbord-filters-board"]
)
router.include_router(
    medal_routers.router,
    prefix=("/medals"),
    tags=["dashbord-medal-board"]
)

