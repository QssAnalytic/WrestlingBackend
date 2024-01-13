from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.app.schemas.fight_info_schemas import AllFightInfoBase, FightInfoBase
from src.app.crud.crud_fight_infos import fight_info

router = APIRouter()

@router.get("/", response_model=List[AllFightInfoBase])
def fight_infos(db: Session = Depends(get_db)):
    response = fight_info.get_multi(db=db)
    return response

@router.get("/{fight_info_id}", response_model=FightInfoBase)
def get_fight_info(fight_info_id: int, db: Session=Depends(get_db)):
    response = fight_info.get_by_id(id=fight_info_id, db=db)
    return response