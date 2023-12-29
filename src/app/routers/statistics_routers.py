from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

from src.app.schemas.fight_statistic_schemas import CreateFightStatistic

from src.app.crud.crud_statistic import statistic


router = APIRouter()



@router.post("/", response_model=CreateFightStatistic)
def create_fight_statistic(statistic_data: CreateFightStatistic, db: Session = Depends(get_db)):
    stat = statistic.create(data=statistic_data, db=db)
    return stat