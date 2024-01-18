from typing import Optional, List
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session, joinedload

from src.app.crud.base import CRUDBase
from src.app.models import FightStatistic, FightInfo, ActionName, Technique, Fighter
from src.app.schemas.fight_statistic_schemas import CreateFightStatistic, UpdateFightStatistic


class CRUDStatistic(CRUDBase[FightStatistic,CreateFightStatistic,UpdateFightStatistic]):
    def get_by_id(self, action_id: int, db: Session) -> Optional[FightStatistic]:
        data = db.execute(select(FightStatistic)
        .filter(FightStatistic.id == action_id)
        .options(
            joinedload(FightStatistic.fighter)
        )
        ).scalars().first()
        return data
    
    def create_statistic(self, data: CreateFightStatistic, db: Session)-> CreateFightStatistic:
        data_obj = jsonable_encoder(data)
        data_obj['score'] = data_obj.pop('score_id')
        db_data = self.model(**data_obj)
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return db_data


statistic = CRUDStatistic(FightStatistic)