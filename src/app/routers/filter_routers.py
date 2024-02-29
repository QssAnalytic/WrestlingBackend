from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.app.schemas.filter_schemas import WeightOutPutBase, StageOutPutBase, DateOutPutBase, WrestlingStyleOutPutBase

from src.app.crud.crud_filters import filter
from src.app.schemas.tournament_schemas import TournamentBaseInfos
router = APIRouter()

@router.get("/dates/", response_model=List[DateOutPutBase])
def get_dates(db: Session = Depends(get_db)):
    response = filter.get_dates(db=db)
    response_data = [{"date": year} for year in response]

    return response_data


@router.get("/tournaments/", response_model=List[TournamentBaseInfos])
def get_all_tournament(date: Optional[int] = None, db: Session = Depends(get_db)):
    if date != None:
        response = filter.get_multi(date=date,db=db)
    if date == None:
        response = filter.fech_multi(db=db)

    return response

@router.get("/weights/", response_model=List[WeightOutPutBase])
def get_weight_list(tournament_id: Optional[int] = None, wrestling_type: Optional[str] = None, db: Session = Depends(get_db)):
    response = filter.get_weights(tournament_id=tournament_id, wrestling_type=wrestling_type, db=db)
    return response


@router.get("/style/", response_model=List[WrestlingStyleOutPutBase])
def get_weight_type(tournament_id: Optional[int] = None, db: Session = Depends(get_db)):
    response = filter.get_wrestling_type(tournament_id=tournament_id, db=db)
    return response


@router.get("/stages/", response_model=List[StageOutPutBase])
def get_stage_list(weight: Optional[int] = None, db: Session = Depends(get_db)):
    response = filter.get_stages(weight=weight, db=db)
    return response

