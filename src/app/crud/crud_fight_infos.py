from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from src.app.crud.base import CRUDBase
from src.app.models import FightInfo, FightStatistic
from src.app.schemas.fight_info_schemas import CreateFighterInfo, UpdateFighterInfo
from src.app.helpers import FightInfoPagination

class CRUDFightInfos(CRUDBase[FightInfo,CreateFighterInfo, UpdateFighterInfo]):

    def get_multi(self, db:Session, page:Optional[int], limit: int) -> List[FightInfo]:
        data = db.query(FightInfo) 
        pagination = FightInfoPagination(session=db, page=page, limit=limit, query = data) 
        return pagination.get_response()

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


fight_info = CRUDFightInfos(FightInfo)