from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base

ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)

def pin_to_parter_escape_rate_utils(engine, params: dict):
    statement = text("""
        with total as (
        select f.opponent_id, count(*) as total_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id
        group by f.opponent_id
        ),
        success as (
        select f.opponent_id, count(*) as successful_escape from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = false 
        group by f.opponent_id
        )
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) pin_to_parter_escape_rate
        from total t left join success s on s.opponent_id = t.opponent_id  where t.opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        pin_to_parter_escape_rate = conn.execute(statement, params)
    return pin_to_parter_escape_rate.fetchone()


def takedown_escape_rate_utils(engine, params: dict):
    statement = text("""
            with total as (
            select f.opponent_id, count(*) as total_count from fightstatistics f
          	inner join fightinfos f2 on f.fight_id = f2.id
                
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id
                group by f.opponent_id
                ),
                success as (
                select f.opponent_id, count(*) as successful_escape from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
   
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = false 
                group by f.opponent_id
                )
            select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) takedown_parter_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id where t.opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        takedown_escape_rate = conn.execute(statement, params)
    return takedown_escape_rate.fetchone()