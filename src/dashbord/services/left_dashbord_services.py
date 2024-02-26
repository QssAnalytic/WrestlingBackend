from datetime import datetime
from typing import Generic, TypeVar, Type
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Integer, desc, func, select, text, or_, and_, case, extract
from sqlalchemy.orm import Session
from src.app.models import FightInfo
from database import Base, engine

ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)



class MedalLeftDashbordSerivices(Generic[ModelTypeVar]):
    def __init__(self, model: Type[ModelTypeVar], engine) -> None:
        self.model = model
        self.engine = engine

    def takedown_count(self, params: dict):
            statement = text("""
                with total as (
                select f.fighter_id, name, count(*) as total_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                inner join actions a on f.action_name_id = a.id
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id --action_filter
                group by f.fighter_id, a.name 
                ),

                success as (
                select f.fighter_id, name, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                inner join actions a on f.action_name_id = a.id
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
                group by f.fighter_id, a.name 

                ),

                unsuccess as (
                select f.fighter_id, name, count(*) as unsuccessful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                inner join actions a on f.action_name_id = a.id
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = false
                group by f.fighter_id, a.name 
                )
                select * from (select *, round(1 - cast(t_rank as decimal) / cast(max(t_rank) over() as decimal), 2) from( 
                select *, dense_rank() over (order by percentage desc) t_rank
                from(
                select t.fighter_id, total_count, coalesce(successful_count, 0) as successful_count,
                        coalesce(unsuccessful_count, 0) as unsuccessful_count, coalesce(cast (successful_count as decimal)/cast(total_count as decimal), 0) as percentage
                        from total t
                left join success s
                on t.fighter_id = s.fighter_id
                left join unsuccess u
                on t.fighter_id = u.fighter_id
                )))
                where fighter_id = :fighter_id
                """)
            with self.engine.connect() as conn:
                takedown_count = conn.execute(statement, params)
            return takedown_count
    

    def average_takedowns_per_match(self, params: dict):
         statement = text("""
            with action_counts as (select fighter_id, count(f2.action_name_id) as tkd_counts
            from fightstatistics f2 where f2.action_name_id = :action_name_id and  f2.successful = true and 
            group by fighter_id),

            match_counts as (select fighter_id, count(distinct id) as m_counts from fightstatistics f2 
            group by fighter_id)

            select * from (select *, round(1 - cast(t_rank as decimal) / cast(max(t_rank) over() as decimal), 2) from(
            select *, rank() over(order by avg_takedowns desc) t_rank from (
            select m.fighter_id, coalesce(cast(tkd_counts as decimal) / cast(m_counts as decimal), 0) avg_takedowns from action_counts a 
            right join match_counts m 
            on a.fighter_id = m.fighter_id)))
            """)
         with self.engine.connect() as conn:
              average_takedowns_per_match = conn.execute(statement, params)
                 
            
    

medal_left_dashbord_service = MedalLeftDashbordSerivices(FightInfo, engine)