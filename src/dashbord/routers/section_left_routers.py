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



# @router.get("/metrics/", response_model=List[MetricsOutPut])
# def metrics(fight_date: str, action_name_id: int, fighter_id: int, db: Session = Depends(get_db)):
#     fight_date = tuple(list(map(int, fight_date.split(","))))
#     params = {"fight_date": fight_date, "action_name_id": action_name_id, "fighter_id": fighter_id}
#     response_list = []
#     res_obj = {"name": None, "metrics":None}
#     response_list, = medal_left_dashbord_service.takedown_statistic(params=params, db=db)
#     return response_list


@router.get("/metrics/")
def metrics(fight_date: str, fighter_id: int, db: Session = Depends(get_db)):
    fight_date = tuple(list(map(int, fight_date.split(","))))
    params = {"fight_date": fight_date,  "fighter_id": fighter_id}
    response_list = []
    takedown_obj = medal_left_dashbord_service.takedown_statistic(params=params, db=db)
    defence_reason_obj = medal_left_dashbord_service.defence_score_statistic(params=params, db=db)
    offense_score_obj = medal_left_dashbord_service.offense_score_statistic(params=params, db=db)
    response_list.append(takedown_obj)
    response_list.append(defence_reason_obj)
    response_list.append(offense_score_obj)
    return response_list

@router.get("/stats/")
def metrics(fight_date: str, fighter_id: int, db: Session = Depends(get_db)):
    fight_date = tuple(list(map(int, fight_date.split(","))))
    params = {"fight_date": fight_date,  "fighter_id": fighter_id}