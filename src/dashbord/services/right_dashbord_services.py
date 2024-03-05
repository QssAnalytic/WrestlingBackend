from datetime import datetime
from typing import Generic, TypeVar, Type
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Float, Integer, desc, func, select, text, or_, and_, case, extract, cast, outerjoin, literal_column, distinct
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session
from src.app.models import FightInfo
from database import Base, session_factory

ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)



class MedalRightDashbordSerivices(Generic[ModelTypeVar]):
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
            "win_rate": 0,
            "score_by_weight": 0

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

        # wins = db.query(
        #     FightInfo.fighter_id,
        #     func.count().label('win_matches')
        # ).filter(
        #     FightInfo.weight_category == 97
        # ).group_by(
        #     FightInfo.fighter_id
        # ).cte()

        # loses = db.query(
        #     FightInfo.oponent_id,
        #     func.count().label('lose_matches')
        # ).filter(
        #     FightInfo.weight_category == 97
        # ).group_by(
        #     FightInfo.oponent_id
        # ).cte()

        # full_join = db.query(
        #     func.coalesce(wins.c.fighter_id, loses.c.oponent_id).label('fighter_id'),
        #     func.coalesce(wins.c.win_matches, 0).label('wins'),
        #     func.coalesce(loses.c.lose_matches, 0).label('loses')
        # ).outerjoin(
        #     wins, wins.c.fighter_id == loses.c.oponent_id
        # ).subquery()


        # percentage = db.query(
        #     full_join.c.fighter_id,
        #     func.round(
        #         func.cast(full_join.c.wins, Float) / func.cast(full_join.c.wins + full_join.c.loses, Float),
        #         2
        #     ).label('percentage')
        # ).all()
        query = db.query(distinct(FightInfo.weight_category)).filter((FightInfo.fighter_id == fighter_id) | (FightInfo.oponent_id == fighter_id))
        unique_weight_categories = tuple([result[0] for result in query.all()])
        params = {"fighter_id": fighter_id, "weight_category":unique_weight_categories, "fight_date": year}
        statement = text("""
        -- win_percentage_percentile
            with 
            wins as (
            select fighter_id, count(*) win_matches from fightinfos where weight_category in :weight_category and extract(year from fight_date) = :fight_date group by fighter_id
            ),
            loses as (
            select oponent_id, count(*) lose_matches from fightinfos where weight_category in :weight_category and extract(year from fight_date) = :fight_date group by oponent_id 
            )
            select * from (
            select *, round(1 - cast(ranks as decimal) / cast(max(ranks) over() as decimal), 2) 
            from (
            select *, rank() over(order by percentage desc) ranks 
            from (
            select fighter_id, round(cast(wins as decimal) / cast(total as decimal), 2) percentage 
            from(
            select fighter_id, wins, wins + loses total 
            from(
            select coalesce(fighter_id, oponent_id) fighter_id, coalesce(win_matches,0) wins , coalesce(lose_matches, 0)loses from loses l full outer join wins w
            on w.fighter_id = l.oponent_id))))) where fighter_id = :fighter_id
        """)
        with session_factory() as session:
            stats_takedown = session.execute(statement, params)
            fetch = stats_takedown.fetchone()
        
        if fetch is not None:
            
            response_obj["score_by_weight"] = float(fetch[-1])

        return response_obj
    
    def get_total_points(self, fighter_id: int, year: str, db: Session) -> dict:
        years = list(map(int,year.split(",")))
        response_obj = {
            "gained":[],
            "skipped": []
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
        # total_average = round(gained_points / all_fight_count, 1)
        # average_skip = round(skipped_points / all_fight_count, 1)
        total_average = 5
        average_skip = 2
        gained_obj['total_points'] = gained_points
        gained_obj['avg_points'] = total_average
        skipped_obj['total_points'] = skipped_points
        skipped_obj['avg_points'] = average_skip
        response_obj['gained'].append(gained_obj)
        response_obj['skipped'].append(skipped_obj)
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
    

medal_right_dashbord_service = MedalRightDashbordSerivices(FightInfo)


