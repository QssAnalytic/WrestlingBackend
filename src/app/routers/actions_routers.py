from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from database import get_db
from src.app.schemas.action_schemas import ActionNameCreate, ActionBaseInfos
from src.app.models import ActionName
from src.app.crud.crud_statistic import statistic

router = APIRouter()


@router.get("/", response_model=List[ActionBaseInfos])
def get_all_actions(db: Session = Depends(get_db)):
    actions = db.execute(
        select(ActionName)
    )
    response = actions.scalars().all()
    return response

@router.post('/', response_model=ActionNameCreate)
def create_action(action: ActionNameCreate, db: Session = Depends(get_db)):
    action = ActionName(**action.dict())
    db.add(action)
    db.commit()
    db.refresh(action)
    return action