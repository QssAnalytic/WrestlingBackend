from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database import get_db
from src.app.models import FightInfo, Fighter
from src.app.schemas.fight_info_schemas import AllFightInfoBase, FightInfoBase, FightInfoOut, CreateFighterInfoBase
from src.app.crud.crud_fight_infos import fight_info

router = APIRouter()

@router.get("/", response_model=FightInfoOut)
def fight_infos(tournament_id: int | None = None, place: str | None = None, wrestler_name: str | None = None,
                author: str | None = None, is_submitted: bool | None = None, status: str | None = None,
                weight_category: int | None = None, date: int | None = None, stage: str | None = None,
                page: Optional[int]= Query(1, ge=0),limit:int=Query(100, ge=100),db: Session = Depends(get_db)):
    query = db.query(FightInfo)
    
    fighter_ids=db.query(Fighter.id).filter(func.upper(Fighter.name) == func.upper(wrestler_name))
    
    if stage is not None:
        query = query.filter(FightInfo.stage == stage)
    if tournament_id is not None:
        query = query.filter(FightInfo.tournament_id == tournament_id)
    if place is not None:
        query = query.filter(FightInfo.location == place)
    if wrestler_name is not None:
        query = query.filter(or_(FightInfo.fighter_id.in_(fighter_ids), FightInfo.oponent_id.in_(fighter_ids)))
    if author is not None:
        query = query.filter(func.upper(FightInfo.author) == func.upper((author)))
    if is_submitted is not None:
        query = query.filter(FightInfo.is_submitted == is_submitted)
    if status is not None:
        query = query.filter(FightInfo.status == status)
    if date is not None:
        query = query.filter(func.extract("year", FightInfo.fight_date) == date)

    if weight_category is not None:
        query = query.filter(FightInfo.weight_category == weight_category)
    response = fight_info.get_multi(db=db, page=page, limit=limit, data=query)
    return response

@router.post("/", response_model=FightInfoBase)
def create_fight_info(data: CreateFighterInfoBase, db: Session = Depends(get_db)):
    response  = fight_info.create_fightinfo(data=data, db=db)
    return response

@router.get("/{fight_info_id}", response_model=FightInfoBase)
def get_fight_info(fight_info_id: int, db: Session=Depends(get_db)):
    response = fight_info.get_by_id(id=fight_info_id, db=db)
    return response

@router.put("/status/{fight_info_id}")
def change_fight_info_status(fight_info_id: int, db: Session=Depends(get_db)):
    fight_info = db.query(FightInfo).filter(FightInfo.id == fight_info_id).first()
    fight_info.status = "completed"
    db.commit()
    return "completed"


@router.put("/check/{fight_info_id}")
def change_fight_info_submit(fight_info_id: int, db: Session=Depends(get_db)):
    fight_info = db.query(FightInfo).filter(FightInfo.id == fight_info_id).first()
    fight_info.is_submitted = True
    fight_info.status = "checked"
    db.commit()
    return "checked"


