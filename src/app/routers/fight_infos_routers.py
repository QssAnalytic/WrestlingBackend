from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from database import get_db
from src.app.schemas.fight_info_schemas import AllFightInfoBase
from src.app.schemas.fight_statistic_schemas import CreateFightStatistic
from src.app.models import FightInfo
from src.app.crud.crud_statistic import statistic



router = APIRouter()

@router.get("/", response_model=List[AllFightInfoBase])
def get_fight_infos(db: Session = Depends(get_db)):
    response = db.execute(
        select(FightInfo).options(
        joinedload(FightInfo.fighter),
        joinedload(FightInfo.oponent),
        joinedload(FightInfo.winner),
    )
    ).scalars().unique().all()


    return response

