from fastapi import APIRouter
from src.dashbord.routers import filter_routers, section_right_routers, section_right_routers, section_left_routers
router = APIRouter()

router.include_router(
    filter_routers.router,
    prefix=("/filters"),
    tags=["dashbord-filters-board"]
)
router.include_router(
    section_right_routers.router,
    prefix=("/section-right"),
    tags=["dashbord-medal-board"]
)

router.include_router(
    section_left_routers.router,
    prefix=("/section-left"),
    tags=["dashbord-medal-board"]
)