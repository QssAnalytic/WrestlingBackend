from fastapi import APIRouter
from src.app.routers import actions_routers, fight_infos_routers, statistics_routers, technique_routers, filter_routers


router = APIRouter()

router.include_router(
    fight_infos_routers.router,
    prefix="/fight-infos",
    tags=["fight-infos"]
)

router.include_router(
    statistics_routers.router,
    prefix="/statistics",
    tags=["statistics"]
)
router.include_router(
    actions_routers.router,
    prefix="/actions",
    tags=["actions"]
)

router.include_router(
    technique_routers.router,
    prefix="/techniques",
    tags=["techniques"]
)
router.include_router(
    filter_routers.router,
    prefix="/filters",
    tags=["filters"]
)
