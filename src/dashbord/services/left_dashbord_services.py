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
        action = db.query(ActionName).filter(ActionName.name == "Pin to parter").first()
        obj = {}
        params['action_name_id'] = action.id
        response_list = []
        defence_score_sum = 0
        pin_to_parter_escape_rate_string = "Pin to parter escape rate"
        takedown_escape_rate_string = "Takedown escape rate"
        pin_to_parter_escape_rate = pin_to_parter_escape_rate_utils(engine=self.engine, params=params)
        takedown_escape_rate = takedown_escape_rate_utils(engine=self.engine, params=params)

        if takedown_escape_rate is not None:
            response_list.append({"metrics": takedown_escape_rate_string,"score": takedown_escape_rate[-1]})
        else: response_list.append({"metrics": takedown_escape_rate_string,"score": 0})


        if pin_to_parter_escape_rate is not None:
            response_list.append({"metrics": pin_to_parter_escape_rate_string,"score": pin_to_parter_escape_rate[-1]})
            defence_score_sum+=float(pin_to_parter_escape_rate[-1])
        else: response_list.append({"metrics": pin_to_parter_escape_rate_string,"score": 0})

        obj["name"] = "Defence Score"
        obj["metrics"] = response_list
        obj["avg"] = round(defence_score_sum/float(len(response_list)),2)*100
        return obj

    def takedown_statistic(self, params: dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == "Takedown").first()
        obj = {}
        params['action_name_id'] = action.id
        response_list = []
        take_down_sum = 0
        takedown_success_rate = takedown_success_rate_utils(engine=self.engine, params=params)
        takedown_per_match = takedown_per_match_utils(engine=self.engine, params=params)
        takedown_average_points_per_fight = takedown_average_points_per_fight_utils(engine=self.engine, params=params)
        takedown_count = takedown_count_utils(engine=self.engine, params=params)
        double_leg_takedown_count = double_leg_takedown_count_utils(engine=self.engine, params=params,model=self.model, db=db)
        single_leg_takedown_success_rate = single_leg_takedown_success_rate_utils(engine=self.engine, params=params, model=self.model, db=db)
        single_leg_takedown_count = single_leg_takedown_count_utils(engine=self.engine, params=params, model=self.model, db=db)
        double_leg_takedown_success_rate = double_leg_takedown_success_rate_utils(engine=self.engine, params=params, model=self.model, db=db)

        takedown_success_rate_string = "Takedown Success rate"
        takedown_per_match_string = "Takedown per fight total"
        takedown_average_points_per_fight_string  = "Average takedown points per fight"
        takedown_count_string = "Takedown Count"
        single_leg_takedown_count_string = "Single leg takedown count"
        single_leg_takedown_success_rate_string = "Singe Leg takedown Success Rate"
        double_leg_takedown_count_string = "Double leg takedown counts"
        double_leg_takedown_success_rate_string = "Double leg takedown"


        if takedown_success_rate is not None:
            response_list.append({"metrics": takedown_success_rate_string,"score": takedown_success_rate[-1]})
            take_down_sum+=float(takedown_success_rate[-1])
        else: response_list.append({"metrics": takedown_success_rate_string,"score": 0})

        if takedown_per_match is not None:
            response_list.append({"metrics": takedown_per_match_string,"score": takedown_per_match[-1]})
            take_down_sum+=float(takedown_per_match[-1])
        else: response_list.append({"metrics": takedown_per_match_string,"score": 0})

        if takedown_average_points_per_fight is  not None:
            response_list.append({"metrics": takedown_average_points_per_fight_string,"score": takedown_average_points_per_fight[-1]})
            take_down_sum+=float(takedown_average_points_per_fight[-1])
        else: response_list.append({"metrics": takedown_average_points_per_fight_string,"score": 0})

        if takedown_count is not None:
            response_list.append({"metrics": takedown_count_string,"score": takedown_count[-1]})
            take_down_sum+=float(takedown_count[-1])
        else: response_list.append({"metrics": takedown_count_string,"score": 0})

        if double_leg_takedown_count is not None:
            response_list.append({"metrics":double_leg_takedown_count_string,"score": double_leg_takedown_count[-1]})
            take_down_sum+=float(double_leg_takedown_count[-1])
        else: response_list.append({"metrics":double_leg_takedown_count_string,"score": 0})

        if double_leg_takedown_success_rate is not None:
            response_list.append({"metrics":double_leg_takedown_success_rate_string,"score": double_leg_takedown_success_rate[-1]})
            take_down_sum+=float(double_leg_takedown_success_rate[-1])
        else: response_list.append({"metrics":double_leg_takedown_success_rate_string,"score": 0})

        if single_leg_takedown_success_rate is not None:
            response_list.append({"metrics":single_leg_takedown_success_rate_string,"score": single_leg_takedown_success_rate[-1]})
            take_down_sum+=float(single_leg_takedown_success_rate[-1])
        else: response_list.append({"metrics":single_leg_takedown_success_rate_string,"score": 0})
        
        if single_leg_takedown_count is not None:
            response_list.append({"metrics":single_leg_takedown_count_string,"score": single_leg_takedown_count[-1]})
            take_down_sum+=float(single_leg_takedown_count[-1])
        else: response_list.append({"metrics":single_leg_takedown_count_string,"score": 0})
        obj["name"] = "Takedown Score"
        obj["metrics"] = response_list
        obj["avg"] = round(take_down_sum/float(len(response_list)),2)*100
        return obj

    
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