
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database import get_db
from src.app.models import FightInfo, Fighter
from src.app.schemas.fight_info_schemas import AllFightInfoBase, FightInfoBase, FightInfoOut, CreateFighterInfoBase\
,UpdateFighterInfo, UpdateFightInfoAuthorStatusOrder
from src.app.crud.crud_fight_infos import fight_info
from src.app.helpers import get_currenct_date
router = APIRouter()

@router.get("/", response_model=FightInfoOut)
def fight_infos(tournament_id: int | None = None, place: str | None = None, wrestler_name: str | None = None,
                author: str | None = None, is_submitted: bool | None = None, status: str | None = None,
                weight_category: int | None = None, date: int | None = None, stage: str | None = None,
                wrestling_type: str | None = None,
                page: Optional[int]= Query(1, ge=0),limit:int=Query(100, ge=100),db: Session = Depends(get_db)):
    query = db.query(FightInfo)
    
    
    if wrestling_type is not None:
        query = query.filter(FightInfo.wrestling_type == wrestling_type)
    if stage is not None:
        query = query.filter(FightInfo.stage == stage)
    if tournament_id is not None:
        query = query.filter(FightInfo.tournament_id == tournament_id)
    if place is not None:
        query = query.filter(FightInfo.location == place)
    if wrestler_name is not None:
        fighter_ids=db.query(Fighter.id).filter(func.upper(Fighter.name) == func.upper(wrestler_name))
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
    response  = fight_info.create_fight_info(data=data, db=db)
    return response

@router.get("/{fight_info_id}", response_model=FightInfoBase)
def get_fight_info(fight_info_id: int, db: Session=Depends(get_db)):
    response = fight_info.get_by_id(id=fight_info_id, db=db)
    return response


@router.put("/{fight_info_id}")
def change_fight_info(fight_info_id: int, data: UpdateFighterInfo, db: Session=Depends(get_db)):
    response = fight_info.update(id=fight_info_id, data=data ,db = db)
    return response

# @router.put("/status/")
# def change_fight_info_status(status: str, fight_info_id: int, db: Session=Depends(get_db)):
#     fight_info = db.query(FightInfo).filter(FightInfo.id == fight_info_id).first()
    
#     current_date = get_currenct_date()
#     status_list = ["completed", "in progress", "not started", "checked"]
#     if fight_info == None:
#         return HTTPException(status_code=404, detail="content not found")
#     if status not in status_list:
#         return HTTPException(status_code=404, detail="wrong data")
#     if status == "completed":
#         if fight_info.submited_date is None:
#             fight_info.submited_date = current_date
#         fight_info.status = status
#         fight_info.is_submitted = False
#     elif status == "in progress":
#         fight_info.status = status
#         fight_info.is_submitted = False
#     elif status == "not started":
#         fight_info.status = status
#         fight_info.is_submitted = False

#     elif status == "checked":
#         fight_info.checked_date = current_date
#         fight_info.is_submitted = True
#         fight_info.status = "checked"
#     db.commit()
#     db.refresh(fight_info)
#     return fight_info.status

@router.put("/state/{fight_info_id}/", response_model=UpdateFightInfoAuthorStatusOrder)
def change_fight_info_athor_order(fight_info_id: int, data: UpdateFightInfoAuthorStatusOrder, db:Session = Depends(get_db)):
    response = fight_info.update(id=fight_info_id, data=data, db=db)
    return response


    


