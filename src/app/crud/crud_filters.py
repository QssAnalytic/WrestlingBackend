from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, extract, cast, func, Integer, and_
from src.app.crud.base import CRUDBase
from src.app.models import Tournament, FightInfo, Fighter
from src.app.schemas.tournament_schemas import TournamentBaseInfos

class CRUDFilter(CRUDBase[Tournament,TournamentBaseInfos, TournamentBaseInfos]):
    
    def get_weights(self, tournament_id: Optional[int], wrestling_type: Optional[str], db: Session):
        query = select(FightInfo)

        if tournament_id is not None:
            query = query.filter(FightInfo.tournament_id == tournament_id)

        if wrestling_type is not None:
            query = query.filter(FightInfo.wrestling_type == wrestling_type)

        data = db.execute(
            query.distinct(FightInfo.weight_category)
                .order_by(FightInfo.weight_category)
        ).scalars().all()
        return data
    
    def get_wrestling_type(self, tournament_id: Optional[int], db: Session):
        query = select(FightInfo)
        if tournament_id != None:
            query = query.filter(FightInfo.tournament_id == tournament_id)
        data = db.execute(query.distinct(FightInfo.wrestling_type)
        ).scalars().all()
        return data

    def get_dates(self, db: Session):
        data = db.execute(
            select(func.extract('year', Tournament.date).cast(Integer)).distinct().order_by(func.extract('year', Tournament.date).cast(Integer))
        ).scalars().all()
        return data
    
    def get_stages(self, weight: Optional[int], db: Session):
        query = select(FightInfo)
        if weight !=None:
            query = query.filter(FightInfo.weight_category == weight)
        data = db.execute(query.distinct(FightInfo.stage)
        ).scalars().all()
        return data
    
    def get_fightinfos(self, date:int, db:Session):
        data = db.execute(select(FightInfo).filter(func.extract('year',FightInfo.date).cast(Integer) == date)).scalars().all()
        return data
    
    def get_multi(self, date:int, db:Session):
        data = db.execute(select(Tournament).filter(func.extract('year',Tournament.date).cast(Integer) == date)).scalars().all()
        return data
    

filter = CRUDFilter(Tournament)