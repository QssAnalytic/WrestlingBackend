from typing import Generic, TypeVar, Type
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Integer, desc, func, select, text, or_, and_
from sqlalchemy.orm import Session
from src.app.models import FightInfo
from database import Base
from pprint import pprint
ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)



class MedalDasgbordSerivices(Generic[ModelTypeVar]):
    def __init__(self, model: Type[ModelTypeVar]) -> None:
        self.model = model

    
    def get_medals_count(self, fighter_id: int, year: int, db: Session):
        result_obj = {
            "Gold": 0,
            "Bronze": 0,
            "Silver": 0
        }
        gold_bronze_medal_count = db.query(self.model.stage, func.count().label('stage_count'))\
            .filter(self.model.stage.in_(['Gold', 'Bronze']))\
            .filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                ),func.extract('year', self.model.fight_date) == year))\
                .group_by(self.model.stage).all()
        silver_medal_count = db.query(self.model.oponent_id, func.count())\
        .filter(and_(
            self.model.oponent_id == fighter_id,
            self.model.stage == 'Gold',
            func.extract('year', self.model.fight_date) == year))\
                .group_by(self.model.oponent_id).all()
        if silver_medal_count != []:
            for op_id, medal_count in silver_medal_count:
                result_obj['Silver'] = medal_count

        for stage, stage_count in gold_bronze_medal_count:
            result_obj[stage] = stage_count
        return result_obj
    
    def get_medals_list(self, fighter_id: int, year: int, db: Session):
        gold_bornc_place = db.query(
            self.model
        ).filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                ),
                func.extract('year', self.model.fight_date) == year),
                self.model.stage.in_(['Gold', 'Bronze'])
                )\
                .order_by(desc(self.model.stage)).all()
        
        silver_place = db.query(
            self.model
            ).filter(and_(
                self.model.oponent_id == fighter_id,
                func.extract('year', self.model.fight_date) == year),
                self.model.stage == 'Gold').all()
    
        return gold_bornc_place, silver_place
    
    def get_fights_count(self, fighter_id: int, year: int, db: Session):
        response_obj = {
            "win": 0,
            "lose": 0,
            "all_fights": 0

        }
        all_fight_count = db.query(self.model,)\
        .filter(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                )).count()
        win_fight_count = db.query(self.model,)\
        .filter(or_(
                self.model.fighter_id == fighter_id
                )).count()
        lose_fight_count = all_fight_count - win_fight_count
        response_obj['all_fights'] = all_fight_count
        response_obj['win'] = win_fight_count
        response_obj['lose'] = lose_fight_count
        return response_obj
medal_dashbord_service = MedalDasgbordSerivices(FightInfo)