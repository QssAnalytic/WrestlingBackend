from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.app.schemas.filter_schemas import WeightOutPutBase, StageOutPutBase, DateOutPutBase

from src.app.crud.crud_filters import filter
from src.app.schemas.tournament_schemas import TournamentBaseInfos
router = APIRouter()

@router.get("/dates/", response_model=List[DateOutPutBase])
def get_dates(db: Session = Depends(get_db)):
    response = filter.get_dates(db=db)
    response_data = [{"date": year} for year in response]

    return response_data




@router.get("/tournaments/{date}/", response_model=List[TournamentBaseInfos])
def get_all_tournament(date: int, db: Session = Depends(get_db)):
    data = filter.get_multi(date=date,db=db)
    return data


@router.get("/weights/{tournament_id}/", response_model=List[WeightOutPutBase])
def get_weight_list(tournament_id: int, db: Session = Depends(get_db)):
    response = filter.get_weights(tournament_id=tournament_id, db=db)
    print(response)
    return response



@router.get("/stages/{weight}/", response_model=List[StageOutPutBase])
def get_stage_list(weight: int, db: Session = Depends(get_db)):
    response = filter.get_stages(weight=weight, db=db)
    return response

