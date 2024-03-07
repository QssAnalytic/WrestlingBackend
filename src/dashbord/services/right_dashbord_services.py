from datetime import datetime
from typing import Generic, TypeVar, Type
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Float,Numeric, desc, func, text, or_, and_, case, extract, cast, outerjoin, distinct

from sqlalchemy.orm import Session
from src.app.models import FightInfo
from database import Base, session_factory

ModelTypeVar = TypeVar('ModelTypeVar', bound=Base)



class MedalRightDashbordSerivices(Generic[ModelTypeVar]):
    def __init__(self, model: Type[ModelTypeVar]) -> None:
        self.model = model

    
    def get_medals_count(self, fighter_id: int, year: str, db: Session):
        result_obj = {
            'Gold': 0,
            'Bronze': 0,
            'Silver': 0
        }
        years = list(map(int,year.split(',')))

        
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
        years = list(map(int,year.split(',')))
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
        years = list(map(int,year.split(',')))
        response_obj = {
            'win': 0,
            'lose': 0,
            'all_fights': 0,
            'win_rate': 0,
            'score_by_weight': 0,
            'score_by_style': 0

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
        response_obj['win_rate'] = round((win_fight_count / all_fight_count) * 100) if all_fight_count != 0 else 0

        weight_category_query = db.query(distinct(self.model.weight_category)).filter((self.model.fighter_id == fighter_id) | (self.model.oponent_id == fighter_id))
        unique_weight_categories = [result[0] for result in weight_category_query.all()]

        wrestling_type_query = db.query(distinct(self.model.wrestling_type)).filter((self.model.fighter_id == fighter_id) | (self.model.oponent_id == fighter_id))
        unique_wrestling_type = [result[0] for result in wrestling_type_query.all()]

        # Query by weight
        wins_by_weight = db.query(
            self.model.fighter_id,
            func.count().label('win_matches')
        ).filter(and_(
            self.model.weight_category.in_(unique_weight_categories), func.extract('year', self.model.fight_date).in_(years))
        ).group_by(
            self.model.fighter_id
        ).subquery()

        loses_by_weight = db.query(
            self.model.oponent_id,
            func.count().label('lose_matches')
        ).filter(and_(
            self.model.weight_category.in_(unique_weight_categories), func.extract('year', self.model.fight_date).in_(years))
        ).group_by(
            self.model.oponent_id
        ).subquery()

        full_join_by_weight = db.query(
            func.coalesce(wins_by_weight.c.fighter_id, loses_by_weight.c.oponent_id).label('fighter_id'),
            func.coalesce(wins_by_weight.c.win_matches, 0).label('wins_by_weight'),
            func.coalesce(loses_by_weight.c.lose_matches, 0).label('loses_by_weight')
        ).outerjoin(
            loses_by_weight, wins_by_weight.c.fighter_id == loses_by_weight.c.oponent_id, full=True
        ).subquery()

        percentage_by_weight = db.query(
            full_join_by_weight.c.fighter_id,
            func.round(
                (cast(full_join_by_weight.c.wins_by_weight, Numeric) / cast(full_join_by_weight.c.wins_by_weight + full_join_by_weight.c.loses_by_weight, Numeric)
                 ), 2)\
                    .label('percentage_by_weight')).cte()
        
        ranks_by_weight = db.query(
            percentage_by_weight.c.fighter_id,
            percentage_by_weight.c.percentage_by_weight,
            func.rank().over(order_by=percentage_by_weight.c.percentage_by_weight.desc()).label('ranks_by_weight')
        ).subquery()

        round_query = db.query(
            ranks_by_weight.c.fighter_id,
            ranks_by_weight.c.percentage_by_weight,
            ranks_by_weight.c.ranks_by_weight,
            func.round(
                (1 - (cast(ranks_by_weight.c.ranks_by_weight, Numeric) / cast(func.max(ranks_by_weight.c.ranks_by_weight).over(), Numeric))), 2
            ).label("finally_round_by_weight")
        ).subquery()

        finally_round_by_weight = db.query(round_query).filter(round_query.c.fighter_id == fighter_id).first()

        # ------------------------------------------------

        # Query by style
        wins_by_style = db.query(
            self.model.fighter_id,
            func.count().label('win_matches')
        ).filter(and_(
            self.model.wrestling_type.in_(unique_wrestling_type), func.extract('year', self.model.fight_date).in_(years))
        ).group_by(
            self.model.fighter_id
        ).subquery()

        loses_by_style = db.query(
            self.model.oponent_id,
            func.count().label('lose_matches')
        ).filter(and_(
            self.model.wrestling_type.in_(unique_wrestling_type), func.extract('year', self.model.fight_date).in_(years))
        ).group_by(
            self.model.oponent_id
        ).subquery()


        full_join_by_style = db.query(
            func.coalesce(wins_by_style.c.fighter_id, loses_by_style.c.oponent_id).label('fighter_id'),
            func.coalesce(wins_by_style.c.win_matches, 0).label('win_matches_style'),
            func.coalesce(loses_by_style.c.lose_matches, 0).label('lose_matches_style')
        ).outerjoin(
            loses_by_style, wins_by_style.c.fighter_id == loses_by_style.c.oponent_id, full=True
        ).subquery()

        percentage_by_style = db.query(
            full_join_by_style.c.fighter_id,
            func.round(
                (cast(full_join_by_style.c.win_matches_style, Numeric) / cast(full_join_by_style.c.win_matches_style + full_join_by_style.c.lose_matches_style, Numeric)
                 ), 2)\
                    .label('percentage_by_style')).cte()
        ranks_by_style = db.query(
            percentage_by_style.c.fighter_id,
            percentage_by_style.c.percentage_by_style,
            func.rank().over(order_by=percentage_by_style.c.percentage_by_style.desc()).label('ranks_by_style')
        ).subquery()
        round_query_by_style = db.query(
            ranks_by_style.c.fighter_id,
            ranks_by_style.c.percentage_by_style,
            ranks_by_style.c.ranks_by_style,
            func.round(
                (1 - (cast(ranks_by_style.c.ranks_by_style, Numeric) / cast(func.max(ranks_by_style.c.ranks_by_style).over(), Numeric))), 2
            ).label("finally_round_by_style")
        ).subquery()

        finally_round_by_style = db.query(round_query_by_style).filter(round_query_by_style.c.fighter_id == fighter_id).first()

        if finally_round_by_weight is not None:
            response_obj['score_by_weight'] = float(finally_round_by_weight[-1])

        if finally_round_by_style is not None:
            response_obj['score_by_style'] = float(finally_round_by_style[-1])

        return response_obj
    
    def get_total_points(self, fighter_id: int, year: str, db: Session) -> dict:
        years = list(map(int,year.split(',')))
        response_obj = {
            'gained':[],
            'skipped': []
            }
        gained_obj = {}
        skipped_obj = {}
        gained_points = db.query(
            func.sum(
                case(
                    (self.model.fighter_id == fighter_id, self.model.oponent1_point),
                    (self.model.oponent_id == fighter_id, self.model.oponent2_point),
                    else_=0
                )
            ).label('point1_total')
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
            ).label('point1_total')
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

        gained_obj['total_points'] = gained_points
        gained_obj['avg_points'] = total_average
        skipped_obj['total_points'] = skipped_points
        skipped_obj['avg_points'] = average_skip
        response_obj['gained'].append(gained_obj)
        response_obj['skipped'].append(skipped_obj)
        
        return response_obj


    def get_decision_point(self, fighter_id: int, year: str, db: Session):
        years = list(map(int,year.split(',')))
        response_obj = {
            'win_decision': {},
            'lose_decision':{}
        }

        win_decision = db.query(
            self.model.decision, func.count(self.model.decision).label('decision_count')
        ).filter(and_(
                self.model.fighter_id == fighter_id),
                func.extract('year', self.model.fight_date).in_(years)).group_by(self.model.decision).all()
        lose_decision = db.query(
            self.model.decision, func.count(self.model.decision).label('decision_count')
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
    

medal_right_dashbord_service = MedalRightDashbordSerivices(FightInfo)


