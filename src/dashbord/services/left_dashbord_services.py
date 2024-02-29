from datetime import datetime
from typing import Generic, TypeVar, Type

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.app.models import FightInfo, Technique, ActionName
from src.dashbord.utils.takedown_utils import *
from src.dashbord.utils.defence_score_utils import *
from database import Base, engine, get_db

ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)



class MedalLeftDashbordSerivices(Generic[ModelTypeVar]):
    def __init__(self, model: Type[ModelTypeVar], engine) -> None:
        self.model = model
        self.engine = engine


    def defence_score_statistic(self, params:dict, db: Session):
        obj = {"metrics": "",
            "score": 0,
            "successful_count":0,
            "total_count":0,
            "bar_pct": 0}
        response_list = []
        response = {}
        response["name"] = "Defence Score"

        action_escape_rate_obj = action_escape_rate_utils(engine=self.engine, params=params, obj = obj, db=db)
        pin_to_parter_escape_rate_obj = pin_to_parter_escape_rate_utils(engine=self.engine, params=params,obj=obj, db=db)
        takedown_escape_rate_obj = takedown_escape_rate_utils(engine=self.engine, params=params,obj = obj, db=db)
        roll_escape_rate_obj= roll_escape_rate_utils(engine=self.engine, params=params,obj=obj, db=db)
        protection_zone_escape_rate_obj = protection_zone_escape_rate_utils(engine=self.engine, params=params,obj=obj, db=db)
        parterre_escape_rate_obj = parterre_escape_rate_utils(engine=self.engine, params=params, obj=obj, model=self.model,db=db)

        response_list.append(action_escape_rate_obj)
        response_list.append(takedown_escape_rate_obj)
        response_list.append(pin_to_parter_escape_rate_obj)
        response_list.append(roll_escape_rate_obj)
        response_list.append(protection_zone_escape_rate_obj)
        response_list.append(parterre_escape_rate_obj)
        response["metrics_list"] = response_list
        return response

    def takedown_statistic(self, params: dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == "Takedown").first()
        params['action_name_id'] = action.id
        obj = {"metrics": "",
            "score": 0,
            "successful_count":0,
            "total_count":0,
            "bar_pct": 0}
        response = {}
        response["name"] = "Takedown Score"
        response_list = []
        takedown_success_rate_obj = takedown_success_rate_utils(engine=self.engine, params=params, obj = obj)
        takedown_per_match_obj = takedown_per_match_utils(engine=self.engine, params=params, obj = obj)
        takedown_average_points_per_fight_obj = takedown_average_points_per_fight_utils(engine=self.engine, params=params, obj = obj)
        takedown_count_obj = takedown_count_utils(engine=self.engine, params=params, obj = obj)
        double_leg_takedown_count_obj = double_leg_takedown_count_utils(engine=self.engine, params=params,model=self.model,obj = obj, db=db)
        single_leg_takedown_success_obj = single_leg_takedown_success_rate_utils(engine=self.engine, params=params, model=self.model, obj=obj, db=db)
        single_leg_takedown_count_obj = single_leg_takedown_count_utils(engine=self.engine, params=params, model=self.model,obj=obj, db=db)
        double_leg_takedown_success_rate_obj = double_leg_takedown_success_rate_utils(engine=self.engine, params=params, model=self.model,obj=obj, db=db)

        response_list.append(takedown_success_rate_obj)
        response_list.append(takedown_per_match_obj)
        response_list.append(takedown_count_obj)
        response_list.append(single_leg_takedown_success_obj)
        response_list.append(single_leg_takedown_count_obj)
        response_list.append(takedown_average_points_per_fight_obj)
        response_list.append(double_leg_takedown_count_obj)
        response_list.append(double_leg_takedown_success_rate_obj)
        response["metrics_list"] = response_list
        return response
    
medal_left_dashbord_service = MedalLeftDashbordSerivices(Technique, engine)


    # def takedown_success_rate(self, params: dict):
    #         statement = text("""
    #         with total as (
    #             select f.fighter_id, count(*) as total_count from fightstatistics f
    #             inner join fightinfos f2 on f.fight_id = f2.id
                
    #             where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id
    #             group by f.fighter_id
    #             ),
    #             success as (
    #             select f.fighter_id, count(*) as successful_count from fightstatistics f
    #             inner join fightinfos f2 on f.fight_id = f2.id
   
    #             where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
    #             group by f.fighter_id
    #             )
    #             select *,round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) avg_takedowns
    #             from success s left join total t on s.fighter_id = t.fighter_id where s.fighter_id = :fighter_id
    #             """)
    #         with self.engine.connect() as conn:
    #             takedown_count = conn.execute(statement, params)
    #         return takedown_count.fetchone()
    

    # def takedown_per_match(self, params: dict):
    #     statement = text("""
    #         with fighter_matches as (
    #         select s.fighter_id, array_agg(distinct fight_id) fighter_array from fightstatistics s
    #             inner join fightinfos i on s.fight_id = i.id
    #             where extract(year from i.fight_date) in :fight_date
    #             group by s.fighter_id 
    #         ),
    #         opponent_matches as (
    #         select s.opponent_id, array_agg(distinct fight_id) opponent_array from fightstatistics s
    #             inner join fightinfos i on s.fight_id = i.id
    #             where extract(year from i.fight_date) in :fight_date
    #             group by s.opponent_id 
    #         ),
    #         com as (select fighter, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
    #         select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array 
    #         from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id
    #         )),
    #         takedowns_count as (select f.fighter_id, count(*) as successful_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         inner join actions a on f.action_name_id = a.id
    #         where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
    #         group by f.fighter_id)
    #         select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match 
    #         from com c left join takedowns_count t on c.fighter = t.fighter_id where fighter= :fighter_id
    #         """)
    #     with self.engine.connect() as conn:
    #         takedown_per_match = conn.execute(statement, params)
    #     return takedown_per_match.fetchone()
    

    # def takedown_average_points_per_fight(self, params: dict):
    #     statement = text("""
    #         with fighter_matches as (
    #         select s.fighter_id, array_agg(distinct fight_id) fighter_array from fightstatistics s
    #             inner join fightinfos i on s.fight_id = i.id
    #             where extract(year from i.fight_date) in :fight_date
    #             group by s.fighter_id 
    #         ),
    #         opponent_matches as (
    #         select s.opponent_id, array_agg(distinct fight_id) opponent_array from fightstatistics s
    #             inner join fightinfos i on s.fight_id = i.id
    #             where extract(year from i.fight_date) in :fight_date
    #             group by s.opponent_id 
    #         ),
    #         com as (select fighter, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
    #         select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array 
    #         from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id
    #         )),
    #         takedowns_count as (select f.fighter_id, sum(score) as successful_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         inner join actions a on f.action_name_id = a.id
    #         where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
    #         group by f.fighter_id)
    #         select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match 
    #         from com c left join takedowns_count t on c.fighter = t.fighter_id where c.fighter = :fighter_id
    #         """)
    #     with self.engine.connect() as conn:
    #         takedown_average_points_per_fight = conn.execute(statement, params)
    #     return takedown_average_points_per_fight.fetchone()
        
    # def takedown_count(self, params: dict):
    #     statement = text("""
    #         select f.fighter_id, count(*) as successful_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true and f2.fighter_id = :fighter_id  
    #         group by f.fighter_id
    #         """)
    #     with self.engine.connect() as conn:
    #         takedown_count = conn.execute(statement, params)
    #     return takedown_count.fetchone()
    

    # def single_leg_takedown_success_rate(self, params:dict, db: Session):
    #     technique = db.query(self.model).filter(self.model.name == "Single leg takedown").first()   
    #     params['technique_id'] = technique.id
    #     statement = text("""
    #         with total as (
    #         select f.fighter_id, count(*) as total_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id --action_filter
    #         group by f.fighter_id 
    #         ),
    #         success as (
    #         select f.fighter_id, count(*) as successful_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true 
    #         group by f.fighter_id 
    #         )
    #         select s.fighter_id,round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) single_leg_success_rate
    #         from success s left join total t on s.fighter_id = t.fighter_id where s.fighter_id = :fighter_id
    #         """)
    #     with self.engine.connect() as conn:
    #         single_leg_takedown_success_rate = conn.execute(statement, params)
    #     return single_leg_takedown_success_rate.fetchone()
    

    # def single_leg_takedown_count(self, params:dict, db: Session):
    #     technique = db.query(self.model).filter(self.model.name == "Single leg takedown").first()
    #     params['technique_id'] = technique.id
    #     statement = text("""
    #         select f.fighter_id, count(*) as successful_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true and f.fighter_id = :fighter_id
    #         group by f.fighter_id
    #         """)
    #     with self.engine.connect() as conn:
    #         single_leg_takedown_count = conn.execute(statement, params)
    #     return single_leg_takedown_count.fetchone()
    

    # def double_leg_takedown_count(self, params:dict, db: Session):
    #     technique = db.query(self.model).filter(self.model.name == "Double leg takedown").first()
        
    #     params['technique_id'] = technique.id
    #     statement = text("""
    #         select f.fighter_id, count(*) as successful_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true and f.fighter_id = :fighter_id
    #         group by f.fighter_id
    #         """)
    #     with self.engine.connect() as conn:
    #         double_leg_takedown_count = conn.execute(statement, params)
    #     return double_leg_takedown_count.fetchone()
    

    
    # def double_leg_takedown_success_rate(self, params:dict, db: Session):
    #     technique = db.query(self.model).filter(self.model.name == "Double leg takedown").first()   
    #     params['technique_id'] = technique.id
    #     statement = text("""
    #         with total as (
    #         select f.fighter_id, count(*) as total_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id --action_filter
    #         group by f.fighter_id 
    #         ),
    #         success as (
    #         select f.fighter_id, count(*) as successful_count from fightstatistics f
    #         inner join fightinfos f2 on f.fight_id = f2.id
    #         where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true 
    #         group by f.fighter_id 
    #         )
    #         select s.fighter_id,round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) single_leg_success_rate
    #         from success s left join total t on s.fighter_id = t.fighter_id where s.fighter_id = :fighter_id
    #         """)
    #     with self.engine.connect() as conn:
    #         double_leg_takedown_success_rate = conn.execute(statement, params)
    #     return double_leg_takedown_success_rate.fetchone()