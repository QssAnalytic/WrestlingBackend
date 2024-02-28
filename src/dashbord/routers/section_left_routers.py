from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import or_
from sqlalchemy.sql import text
from sqlalchemy.orm import Session

from src.dashbord.services.left_dashbord_services import medal_left_dashbord_service
from src.dashbord.schemas.section_left_schemas import MetricsOutPut
from src.dashbord.enums import ActionNameEnum
from database import get_db
router = APIRouter()



@router.get("/metrics/", response_model=List[MetricsOutPut])
def metrics(fight_date: str, action_name_id: int, action_name:ActionNameEnum, fighter_id: int, db: Session = Depends(get_db)):
    fight_date = tuple(list(map(int, fight_date.split(","))))
    params = {"fight_date": fight_date, "action_name_id": action_name_id, "fighter_id": fighter_id}
    response_list = []
    print(action_name)
    if action_name == ActionNameEnum.Takedown:
        response_list = medal_left_dashbord_service.takedown_statistic(params=params, db=db)
    return response_list