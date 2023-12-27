from typing import Annotated, List
from fastapi import APIRouter,  File, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from database import get_db
from src.app.schemas.fighter_schemas import FightInfoBase
from src.app.schemas.action_schemas import ActionNameCreate, ActionBaseInfos
from src.app.models import FightInfo, ActionName


router = APIRouter()

@router.get("/fight-infos", response_model=List[FightInfoBase])
def get_fight_infos(db: Session = Depends(get_db)):
    response = db.execute(
        select(FightInfo).options(
        joinedload(FightInfo.fighter),
        joinedload(FightInfo.oponent),
        joinedload(FightInfo.winner),
    )
    ).scalars().all()

    return response


@router.get("/actions", response_model=List[ActionBaseInfos])
def get_all_actions(db: Session = Depends(get_db)):
    actions = db.execute(
        select(ActionName)
    )
    response = actions.scalars().all()
    return response

@router.post('/actions', response_model=ActionNameCreate)
def create_action(action: ActionNameCreate, db: Session = Depends(get_db)):
    action = ActionName(**action.dict())
    db.add(action)
    db.commit()
    db.refresh(action)
    return action
