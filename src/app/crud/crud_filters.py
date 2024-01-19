from sqlalchemy.orm import Session
from sqlalchemy import select, extract, cast, func, Integer
from src.app.crud.base import CRUDBase
from src.app.models import Tournament, FightInfo, Fighter
from src.app.schemas.tournament_schemas import TournamentBaseInfos

class CRUDTournament(CRUDBase[Tournament,TournamentBaseInfos, TournamentBaseInfos]):
    
    def get_weights(self, tournament_id: int, db: Session):

        data = db.execute(
            select(FightInfo).filter(FightInfo.tournament_id == tournament_id)\
                .distinct(FightInfo.weight_category)\
                    .order_by(FightInfo.weight_category)
        ).scalars().all()
        return data
    
    def get_dates(self, db: Session):
        data = db.execute(
            select(func.extract('year', Tournament.date).cast(Integer)).distinct().order_by(func.extract('year', Tournament.date).cast(Integer))
        ).scalars().all()
        return data
    
    def get_stages(self, weight: int, db: Session):
        data = db.execute(
            select(FightInfo).filter(FightInfo.weight_category == weight)\
                .distinct(FightInfo.stage)
        ).scalars().all()
        return data
    
    
filter = CRUDTournament(Tournament)