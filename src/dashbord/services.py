from datetime import datetime
from typing import Generic, TypeVar, Type
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Integer, desc, func, select, text, or_, and_, case, extract
from sqlalchemy.orm import Session
from src.app.models import FightInfo
from database import Base
from pprint import pprint
ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)



class MedalDashbordSerivices(Generic[ModelTypeVar]):
    def __init__(self, model: Type[ModelTypeVar]) -> None:
        self.model = model

    
    def get_medals_count(self, fighter_id: int, year: str, db: Session):
        result_obj = {
            "Gold": 0,
            "Bronze": 0,
            "Silver": 0
        }
        years = list(map(int,year.split(",")))

        
        gold_bronze_medal_count = db.query(self.model.stage, func.count().label('stage_count'))\
            .filter(self.model.stage.in_(['Gold', 'Bronze']))\
            .filter(and_(
                or_(
                    self.model.fighter_id == fighter_id,
                    self.model.oponent_id == fighter_id
                ),
                func.extract('year', self.model.fight_date).in_(years)
            ))\
            .group_by(self.model.stage).all()
        silver_medal_count = []
        silver_medal_count = db.query(self.model.oponent_id, func.count())\
        .filter(and_(
            self.model.oponent_id == fighter_id,
            self.model.stage == 'Gold',
            func.extract('year', self.model.fight_date).in_(years)))\
                .group_by(self.model.oponent_id).all()
        if silver_medal_count != []:
            for op_id, medal_count in silver_medal_count:
                result_obj['Silver'] = medal_count

        for stage, stage_count in gold_bronze_medal_count:
            result_obj[stage] = stage_count
        return result_obj
    
    def get_medals_list(self, fighter_id: int, year: str, db: Session):
        years = list(map(int,year.split(",")))
        gold_place = db.query(
            self.model
        ).filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                ),
                func.extract('year', self.model.fight_date).in_(years)),
                self.model.stage =='Gold')
                
        bronze_place = db.query(
            self.model
        ).filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                ),
                func.extract('year', self.model.fight_date).in_(years)),
                self.model.stage =='Bronze')
        silver_place = db.query(
            self.model
            ).filter(and_(
                self.model.oponent_id == fighter_id,
                func.extract('year', self.model.fight_date).in_(years)),
                self.model.stage == 'Gold').all()
    
        return gold_place, silver_place, bronze_place


    
    def get_fights_count(self, fighter_id: int, year: str, db: Session):
        years = list(map(int,year.split(",")))
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
                )),func.extract('year', self.model.fight_date).in_(years)).count()
        win_fight_count = db.query(self.model,)\
        .filter(and_(or_(
                self.model.fighter_id == fighter_id
                )),func.extract('year', self.model.fight_date).in_(years)).count()
        lose_fight_count = all_fight_count - win_fight_count
        response_obj['all_fights'] = all_fight_count
        response_obj['win'] = win_fight_count
        response_obj['lose'] = lose_fight_count
        response_obj['win_rate'] = round((win_fight_count / all_fight_count) * 100)
        return response_obj
    
    def get_total_points(self, fighter_id: int, year: str, db: Session) -> dict:
        years = list(map(int,year.split(",")))
        response_obj = {}
        gained_points = db.query(
            func.sum(
                case(
                    (self.model.fighter_id == fighter_id, self.model.oponent1_point),
                    (self.model.oponent_id == fighter_id, self.model.oponent2_point),
                    else_=0
                )
            ).label("point1_total")
        ).filter(
            extract('year', self.model.fight_date).in_(years)
        ).scalar()
        skipped_points = db.query(
            func.sum(
                case(
                    (self.model.fighter_id == fighter_id, self.model.oponent2_point),
                    (self.model.oponent_id == fighter_id, self.model.oponent1_point),
                    else_=0
                )
            ).label("point1_total")
        ).filter(
            extract('year', self.model.fight_date).in_(years)
        ).scalar()
        
        all_fight_count = db.query(self.model)\
        .filter(and_(or_(
                self.model.fighter_id == fighter_id,
                self.model.oponent_id == fighter_id
                )),func.extract('year', self.model.fight_date).in_(years)).count()
        total_average = round(gained_points / all_fight_count, 1)
        average_skip = round(skipped_points / all_fight_count, 1)

        response_obj['total_gained_points'] = gained_points
        response_obj['avg_gained_points'] = total_average
        response_obj['total_skipped_points'] = skipped_points
        response_obj['avg_skipped_points'] = average_skip
        return response_obj


    def get_decision_point(self, fighter_id: int, year: str, db: Session):
        years = list(map(int,year.split(",")))
        response_obj = {
            'win_decision': {},
            'lose_decision':{}
        }

        win_decision = db.query(
            self.model.decision, func.count(self.model.decision).label("decision_count")
        ).filter(and_(
                self.model.fighter_id == fighter_id),
                func.extract('year', self.model.fight_date).in_(years)).group_by(self.model.decision).all()
        lose_decision = db.query(
            self.model.decision, func.count(self.model.decision).label("decision_count")
        ).filter(and_(
                self.model.oponent_id == fighter_id),
                func.extract('year', self.model.fight_date).in_(years)).group_by(self.model.decision).all()
        response_obj['win_decision'] = win_decision
        response_obj['lose_decision'] = lose_decision
        # for w_d in win_decision:
        #     response_obj['win_decision'] = w_d
        # for l_d in lose_decision:
        #     response_obj['lose_decision'] = l_d
        return response_obj
    

medal_dashbord_service = MedalDashbordSerivices(FightInfo)


