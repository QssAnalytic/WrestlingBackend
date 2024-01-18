from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from src.app.models import FightInfo
from src.app.schemas.fight_info_schemas import AllFightInfoBase, FightInfoBase, FightInfoOut
from src.app.crud.crud_fight_infos import fight_info

router = APIRouter()

@router.get("/", response_model=FightInfoOut)
def fight_infos(page: Optional[int]= Query(1, ge=0), limit:int=Query(100, ge=100), db: Session = Depends(get_db)):
    response = fight_info.get_multi(db=db, page=page, limit=limit)
    return response

@router.get("/{fight_info_id}", response_model=FightInfoBase)
def get_fight_info(fight_info_id: int, db: Session=Depends(get_db)):
    response = fight_info.get_by_id(id=fight_info_id, db=db)
    return response

@router.put("/status/{fight_info_id}")
def get_fight_info(fight_info_id: int, db: Session=Depends(get_db)):
    # fight_info = db.query(FightInfo).filter(FightInfo.id == fight_info_id).first()
    # fight_info.status = "smt"
    # db.commit()
    return "Ok"


@router.put("/check/{fight_info_id}")
def get_fight_info(fight_info_id: int, db: Session=Depends(get_db)):
    # fight_info = db.query(FightInfo).filter(FightInfo.id == fight_info_id).first()
    # fight_info.is_submitted = True
    # db.commit()
    return "Ok"