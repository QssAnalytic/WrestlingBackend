from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import or_
from sqlalchemy.sql import text
from sqlalchemy.orm import Session

from src.dashbord.services.left_dashbord_services import medal_left_dashbord_service
from src.dashbord.schemas.section_left_schemas import MetricsOutPut
from src.dashbord.schemas.actions_schemas import ActionoutPut
from src.app.models import ActionName
from database import get_db
router = APIRouter()

@router.get("/metrics-actions", response_model=List[ActionoutPut])
def metrics_actions(db: Session = Depends(get_db)):
    actions = db.query(ActionName).filter(or_(
        ActionName.name == "Takedown",
        ActionName.name == "Roll",
        ActionName.name == "Protection zone",
        ActionName.name == "Pin to parter"
    ))
    return actions

@router.get("/metrics", response_model=List[MetricsOutPut])
def metrics(fight_date: str, action_name_id: int, fighter_id: int, db: Session = Depends(get_db)):
    response_list = []
    fight_date = tuple(list(map(int, fight_date.split(","))))
    params = {"fight_date": fight_date, "action_name_id": action_name_id, "fighter_id": fighter_id}
    takedown_success_rate = medal_left_dashbord_service.takedown_success_rate(params=params)
    takedown_per_match = medal_left_dashbord_service.takedown_per_match(params=params)
    takedown_average_points_per_fight = medal_left_dashbord_service.takedown_average_points_per_fight(params=params)
    takedown_count = medal_left_dashbord_service.takedown_count(params=params)
    double_leg_takedown_count = medal_left_dashbord_service.double_leg_takedown_count(params=params, db=db)
    single_leg_takedown_success_rate = medal_left_dashbord_service.single_leg_takedown_success_rate(params=params, db=db)
    single_leg_takedown_count = medal_left_dashbord_service.single_leg_takedown_count(params=params, db=db)
    double_leg_takedown_success_rate = medal_left_dashbord_service.double_leg_takedown_success_rate(params=params, db=db)

    if takedown_success_rate is not None:
        response_list.append({"metrics":"Takedown success rate","score": takedown_success_rate[-1]})
    else: response_list.append({"metrics":"Takedown success rate","score": 0})

    if takedown_per_match is not None:
        response_list.append({"metrics":"Takedown per match","score": takedown_per_match[-1]})
    else: response_list.append({"metrics":"Takedown per match","score": 0})

    if takedown_average_points_per_fight is  not None:
        response_list.append({"metrics":"Takedown average points per fight","score": takedown_average_points_per_fight[-1]})
    else: response_list.append({"metrics":"Takedown average points per fight","score": 0})

    if takedown_count is not None:
        response_list.append({"metrics":"Takedown count","score": takedown_count[-1]})
    else: response_list.append({"metrics":"Takedown count","score": 0})

    if double_leg_takedown_count is not None:
        response_list.append({"metrics":"Double leg takedown count","score": double_leg_takedown_count[-1]})
    else: response_list.append({"metrics":"Double leg takedown count","score": 0})

    if double_leg_takedown_success_rate is not None:
        response_list.append({"metrics":"Double leg takedown success rate","score": double_leg_takedown_success_rate[-1]})
    else: response_list.append({"metrics":"Double leg takedown success rate","score": 0})

    if single_leg_takedown_success_rate is not None:
        response_list.append({"metrics":"Single leg takedown success rate","score": single_leg_takedown_success_rate[-1]})
    else: response_list.append({"metrics":"Single leg takedown success rate","score": 0})
    
    if single_leg_takedown_count is not None:
        response_list.append({"metrics":"Single leg takedown count","score": single_leg_takedown_count[-1]})
    else: response_list.append({"metrics":"Single leg takedown count","score": 0})


    return response_list