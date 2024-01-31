from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session

from src.dashbord.services import medal_dashbord_service
from src.dashbord.schemas.medals_schemas import MedalsOutPut
from database import get_db

router = APIRouter()


@router.get("/medal-filter/", response_model=MedalsOutPut)
def filter_by_medal(fighter_id: int, year:int, db: Session = Depends(get_db)):
    response = medal_dashbord_service.get_medals_count(fighter_id=fighter_id, year=year, db=db)
    gold_bronze_response, silver_response = medal_dashbord_service.get_medals_list(fighter_id=fighter_id, year=year, db=db)
    response_obj = response
    response_obj['place'] = gold_bronze_response
    response_obj['silver_place'] = silver_response
    return response_obj

@router.get("/get-fight-count/")
def get_all_fight_count(fighter_id: int, year:int, db: Session = Depends(get_db)):
    response  = medal_dashbord_service.get_fights_count(fighter_id=fighter_id, year=year, db=db)
    return response