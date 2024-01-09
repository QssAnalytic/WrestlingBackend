from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

from src.app.schemas.fight_statistic_schemas import CreateFightStatistic, GetFightStatisticBase, UpdateFightStatistic

from src.app.crud.crud_statistic import statistic


router = APIRouter()


@router.get("/{fight_info_id}/{action_number}/", response_model=List[GetFightStatisticBase])
def get_statistic(fight_info_id:int, action_number: str, db: Session = Depends(get_db)):
    response = statistic.get_by_action_number(action_number=action_number, fight_id=fight_info_id, db=db)
    return response

@router.post("/", response_model=CreateFightStatistic)
def create_fight_statistic(statistic_data: CreateFightStatistic, db: Session = Depends(get_db)):
    stat = statistic.create(data=statistic_data, db=db)
    return stat

@router.delete("/{statistic_id}/")
def delete_fight_statistic(statistic_id: int, db: Session = Depends(get_db)):
    statistic.delete(id=statistic_id, db=db)
    return "Succsess"

@router.put("/{statistic_id}/", response_model=UpdateFightStatistic)
def update_fight_statistic(statistic_id: int, statistic_data: UpdateFightStatistic,db: Session = Depends(get_db)):
    updated_data = statistic.update(id = statistic_id,data = statistic_data, db = db)
    return updated_data