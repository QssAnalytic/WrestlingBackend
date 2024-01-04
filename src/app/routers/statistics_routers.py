from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

from src.app.schemas.fight_statistic_schemas import CreateFightStatistic, GetFightStatisticBase

from src.app.crud.crud_statistic import statistic


router = APIRouter()


@router.get("/{fight_info_id}/{action_number}", response_model=List[GetFightStatisticBase])
def get_statistic(fight_info_id:int, action_number: str, db: Session = Depends(get_db)):
    response = statistic.get_by_action_number(action_number=action_number, fight_id=fight_info_id, db=db)
    return response

@router.post("/", response_model=CreateFightStatistic)
def create_fight_statistic(statistic_data: CreateFightStatistic, db: Session = Depends(get_db)):
    stat = statistic.create(data=statistic_data, db=db)
    return stat