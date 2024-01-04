from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, joinedload

from src.app.crud.base import CRUDBase
from src.app.models import FightStatistic
from src.app.schemas.fight_statistic_schemas import CreateFightStatistic


class CRUDStatistic(CRUDBase[FightStatistic,CreateFightStatistic]):
    def get_by_action_number(self, action_number:str, fight_id:int, db: Session) -> Optional[FightStatistic]:
        data = db.execute(select(FightStatistic)
        .filter(and_(FightStatistic.action_number==action_number, FightStatistic.fight_id==fight_id))
        .options(
            joinedload(FightStatistic.fighter),
            joinedload(FightStatistic.technique),
            joinedload(FightStatistic.action_name)
        )
        ).scalars().all()
        return data

statistic = CRUDStatistic(FightStatistic)