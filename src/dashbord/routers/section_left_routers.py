from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.sql import text

from src.dashbord.services.left_dashbord_services import medal_left_dashbord_service
from database import engine
router = APIRouter()

@router.get("/metrics")
def test(fight_date: str, action_name_id: int, fighter_id: int):
    fight_date = tuple(list(map(int, fight_date.split(","))))
    params = {"fight_date": fight_date, "action_name_id": action_name_id, "fighter_id": fighter_id}
    takedown_count = medal_left_dashbord_service.takedown_count(params)
    
    for row in takedown_count:
        return row[-1]
    return "hel"