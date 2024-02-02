from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session

from src.dashbord.services import medal_dashbord_service
from src.dashbord.schemas.section_right_schemas import MedalsOutPut, FightCountsOutPut
from database import get_db

router = APIRouter()


@router.get("/medal-filter/", response_model=MedalsOutPut)
def filter_by_medal(fighter_id: int, year:int, db: Session = Depends(get_db)):
    response = medal_dashbord_service.get_medals_count(fighter_id=fighter_id, year=year, db=db)
    gold_bronze_response, silver_response, bronze_response = medal_dashbord_service.get_medals_list(fighter_id=fighter_id, year=year, db=db)
    response_obj = response
    response_obj['gold_place'] = gold_bronze_response
    response_obj['silver_place'] = silver_response
    response_obj['bronze_place'] = bronze_response

    return response_obj

@router.get("/get-fight-count/", response_model=FightCountsOutPut)
def get_all_fight_count(fighter_id: int, year:int, db: Session = Depends(get_db)):
    response  = medal_dashbord_service.get_fights_count(fighter_id=fighter_id, year=year, db=db)
    return response


@router.get("/get-total-point/")
def get_total_fighter_point(fighter_id: int, year:int, db: Session = Depends(get_db)):
    response_obj = {}
    gained_points, total_average, skipped_points, average_skip  = medal_dashbord_service.get_total_points(fighter_id=fighter_id, year=year, db=db)
    response_obj['gained_points'] = gained_points
    response_obj['total_average'] = total_average
    response_obj['skipped_points'] = skipped_points
    response_obj['average_skip'] = average_skip
    return response_obj