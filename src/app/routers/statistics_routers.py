from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from src.app.schemas.fight_statistic_schemas import CreateFightStatistic, GetFightStatisticBase, UpdateFightStatistic, FightStatisticOutPutBase

from src.app.crud.crud_statistic import statistic


router = APIRouter()


@router.get("/{action_id}/", response_model=FightStatisticOutPutBase)
def get_statistic(action_id:int, db: Session = Depends(get_db)):
    response = statistic.get_by_id(action_id=action_id, db=db)
    if response is None:
        raise HTTPException(status_code=404, detail="Statistic not found")

    return response

@router.post("/", response_model=FightStatisticOutPutBase)
def create_fight_statistic(statistic_data: CreateFightStatistic, db: Session = Depends(get_db)):
    stat = statistic.create_statistic(data=statistic_data, db=db)
    return stat

@router.delete("/{statistic_id}/")
def delete_fight_statistic(statistic_id: int, db: Session = Depends(get_db)):
    statistic.delete(id=statistic_id, db=db)
    return "Succsess"

@router.put("/{statistic_id}/", response_model=FightStatisticOutPutBase)
def update_fight_statistic(statistic_id: int, statistic_data: UpdateFightStatistic,db: Session = Depends(get_db)):
    updated_data = statistic.update_statistic(id = statistic_id,data = statistic_data, db = db)
    return updated_data