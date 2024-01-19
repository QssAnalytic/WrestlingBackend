from typing import Optional, List
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from sqlalchemy import select, and_, update
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
    
    def create_statistic(self, data: CreateFightStatistic, db: Session) -> CreateFightStatistic:
        data_obj = jsonable_encoder(data)
        data_obj['score'] = data_obj.pop('score_id')
        
        db_data = FightStatistic(**data_obj)
        fight_info = db.query(FightInfo).filter(FightInfo.id == data_obj['fight_id']).first()
        fight_info.status = "in progress"
        if fight_info.author is None:
            fight_info.author = data_obj['author']
        
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return db_data
    
    def update_statistic(self, id:int,data: UpdateFightStatistic, db: Session) -> UpdateFightStatistic:
        db_data = self.get(id=id, db=db)
        data_obj = jsonable_encoder(data)
        data_obj['score'] = data_obj.pop('score_id')
        print(data_obj)
        db.execute(
            update(FightStatistic)
            .filter(FightStatistic.id==id)
            .values(**data_obj)
        )
        db.commit()
        db.refresh(db_data)
        return db_data


statistic = CRUDStatistic(FightStatistic)