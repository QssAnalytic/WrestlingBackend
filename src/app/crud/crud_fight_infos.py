from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.app.crud.base import CRUDBase
from src.app.models import FightInfo, FightStatistic
from src.app.schemas.fight_info_schemas import CreateFighterInfo, UpdateFighterInfo

class CRUDStatistic(CRUDBase[FightInfo,CreateFighterInfo, UpdateFighterInfo]):

    def get_multi(self, db:Session) -> List[FightInfo]:
        data = db.execute(
        select(FightInfo).options(
        joinedload(FightInfo.fighter),
        joinedload(FightInfo.oponent),
        joinedload(FightInfo.winner),
        joinedload(FightInfo.tournament)
        ).order_by(FightInfo.id) 
        ).scalars().unique().all()
        return data
    

    def get_by_id(self, id:int, db:Session) -> Optional[FightInfo]:
        data = db.execute(
        select(FightInfo).filter(FightInfo.id==id).options(
        joinedload(FightInfo.fighter),
        joinedload(FightInfo.oponent),
        joinedload(FightInfo.winner),
        joinedload(FightInfo.tournament),
        joinedload(FightInfo.fight_statistic).joinedload(FightStatistic.action_name)
        )
        ).scalars().unique().first()
        return data


fight_info = CRUDStatistic(FightInfo)