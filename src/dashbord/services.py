from typing import Generic, TypeVar, Type
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Integer, desc, func, select, text, or_, and_, case, extract
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
        gold_place = db.query(
            self.model
        ).filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                ),
                func.extract('year', self.model.fight_date) == year),
                self.model.stage =='Gold')
                
        bronze_place = db.query(
            self.model
        ).filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                ),
                func.extract('year', self.model.fight_date) == year),
                self.model.stage =='Bronze')
        silver_place = db.query(
            self.model
            ).filter(and_(
                self.model.oponent_id == fighter_id,
                func.extract('year', self.model.fight_date) == year),
                self.model.stage == 'Gold').all()
    
        return gold_place, silver_place, bronze_place


    
    def get_fights_count(self, fighter_id: int, year: int, db: Session):
        response_obj = {
            "win": 0,
            "lose": 0,
            "all_fights": 0,
            "win_rate": 0

        }
        all_fight_count = db.query(self.model)\
        .filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                )),func.extract('year', self.model.fight_date) == year).count()
        win_fight_count = db.query(self.model,)\
        .filter(and_(or_(
                self.model.fighter_id == fighter_id
                )),func.extract('year', self.model.fight_date) == year).count()
        lose_fight_count = all_fight_count - win_fight_count
        response_obj['all_fights'] = all_fight_count
        response_obj['win'] = win_fight_count
        response_obj['lose'] = lose_fight_count
        response_obj['win_rate'] = round((win_fight_count / all_fight_count) * 100)
        return response_obj
    
    def get_total_points(self, fighter_id: int, year: int, db: Session) -> tuple:
        gained_points = db.query(
            func.sum(
                case(
                    (self.model.fighter_id == fighter_id, self.model.oponent1_point),
                    (self.model.oponent_id == year, self.model.oponent2_point),
                    else_=0
                )
            ).label("point1_total")
        ).filter(
            extract('year', self.model.fight_date) == 2018
        ).scalar()
        skipped_points = db.query(
            func.sum(
                case(
                    (self.model.fighter_id == fighter_id, self.model.oponent2_point),
                    (self.model.oponent_id == year, self.model.oponent1_point),
                    else_=0
                )
            ).label("point1_total")
        ).filter(
            extract('year', self.model.fight_date) == 2018
        ).scalar()
        
        all_fight_count = db.query(self.model)\
        .filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                )),func.extract('year', self.model.fight_date) == year).count()
        total_average = round(gained_points / all_fight_count, 1)
        average_skip = round(skipped_points / all_fight_count, 1)
        return (gained_points, total_average, skipped_points, average_skip)

        
medal_dashbord_service = MedalDasgbordSerivices(FightInfo)


