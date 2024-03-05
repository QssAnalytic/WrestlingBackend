
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database import get_db
from src.app.models import FightInfo, Fighter
from src.app.schemas.fight_info_schemas import AllFightInfoBase, FightInfoBase, FightInfoOut, CreateFighterInfoBase\
,UpdateFighterInfo, UpdateFightInfoAuthorStatusOrder, FilterFightInfoBase
from src.app.crud.crud_fight_infos import fight_info
from src.app.helpers import get_currenct_date
router = APIRouter()

@router.get("/", response_model=FightInfoOut)
def fight_infos(filter_model: FilterFightInfoBase = Depends(),db: Session = Depends(get_db)):
    filter_obj = filter_model.dict()

    query = db.query(FightInfo)
    for k, v in filter_obj.items():

        if v != None and k != 'page' and k != 'limit':
            query = query.filter(getattr(FightInfo, k) == v)


    # if wrestling_type is not None:
    #     query = query.filter(FightInfo.wrestling_type == wrestling_type)
    # if stage is not None:
    #     query = query.filter(FightInfo.stage == stage)
    # if tournament_id is not None:
    #     query = query.filter(FightInfo.tournament_id == tournament_id)
    # if place is not None:
    #     query = query.filter(FightInfo.location == place)
    # if wrestler_name is not None:
    #     fighter_ids = db.query(Fighter.id).filter(func.lower(Fighter.name).like(func.lower(f"{wrestler_name}%")))
    #     query = query.filter(or_(FightInfo.fighter_id.in_(fighter_ids), FightInfo.oponent_id.in_(fighter_ids)))
    # if author is not None:
    #     query = query.filter(func.upper(FightInfo.author) == func.upper((author)))
    # if is_submitted is not None:
    #     query = query.filter(FightInfo.is_submitted == is_submitted)
    # if status is not None:
    #     query = query.filter(FightInfo.status == status)
    # if date is not None:
        # query = query.filter(func.extract("year", FightInfo.fight_date) == date)
    # if weight_category is not None:
    #         query = query.filter(FightInfo.weight_category == weight_category)
    # if check_author is not None:
    #     query = query.filter(FightInfo.check_author == check_author)
    response = fight_info.get_multi(db=db, page=filter_obj['page'], limit=filter_obj['limit'], data=query)
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



@router.put("/state/{fight_info_id}/", response_model=UpdateFightInfoAuthorStatusOrder)
def change_fight_info_athor_order(fight_info_id: int, data: UpdateFightInfoAuthorStatusOrder, db:Session = Depends(get_db)):
    response = fight_info.update_status(id=fight_info_id, data=data, db=db)
    return response

