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
            joinedload(FightStatistic.fighter),
            joinedload(FightStatistic.technique),
            joinedload(FightStatistic.action_name)
        )
        ).scalars().first()
        return data
    
    # def create_statistic(self, fight_statistic: CreateFightStatistic, db: Session)-> CreateFightStatistic:
    #     # fight = db.query(FightInfo).filter(FightInfo.name == fight_statistic.fight_name).first()
    #     action_name = db.query(ActionName).filter(ActionName.name == fight_statistic.action_name).first()
    #     technique = db.query(Technique).filter(Technique.name == fight_statistic.technique_name).first()
    #     fighter = db.query(Fighter).filter(Fighter.name == fight_statistic.fighter_name).first()

    #     fight_info = db.query(FightInfo).first()

    #     # Convert Pydantic model to database model
    #     db_fight_statistic = FightStatistic(
    #         action_time=fight_statistic.action_time,
    #         action_time_second=fight_statistic.action_time_second,
    #         action_number=fight_statistic.action_number,
    #         score=fight_statistic.score,
    #         successful=fight_statistic.successful,
    #         video_second_begin=fight_statistic.video_second_begin,
    #         video_second_end=fight_statistic.video_second_end,
    #         video_link=str(fight_statistic.video_link),
    #         defense_reason=fight_statistic.defense_reason,
    #         fight_id=fight_info.id,
    #         action_name_id=action_name.id,   
    #         technique_id=technique.id,
    #         fighter_id=fighter.id,
    #     )

    #     # Add to database
    #     db.add(db_fight_statistic)
    #     db.commit()
    #     db.refresh(db_fight_statistic)

    #     return {"message": "Fight Statistic created successfully", "data": jsonable_encoder(db_fight_statistic)}
    #     # data_obj = jsonable_encoder(data)
    #     # db_data = self.model(**data_obj)
    #     # db.add(db_data)
    #     # db.commit()
    #     # db.refresh(db_data)
    #     return "db_data"

statistic = CRUDStatistic(FightStatistic)