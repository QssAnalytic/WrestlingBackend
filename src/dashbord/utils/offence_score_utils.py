from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base
from src.app.models import ActionName

def action_success_rate(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
    --action_success_rate
        with total as (
                select f.fighter_id, count(*) as total_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                
                where extract(year from f2.fight_date) in :fight_date
                group by f.fighter_id
                ),
                success as (
                select f.fighter_id, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where extract(year from f2.fight_date) in :fight_date and f.successful = true 
                group by f.fighter_id
                )
            select * from (    
            select fighter_id, takedown_success_rate, successful_count, total_count,round((takedown_success_rate- 0) /(max(takedown_success_rate) over() - 0), 2) bar_pct from 
                (select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 1), 2) takedown_success_rate
                from success s right join total t on s.fighter_id = t.fighter_id))
            where fighter_id = 22638
        """)
    with engine.connect() as conn:
        action_success_rate = conn.execute(statement, params)
    fetch = action_success_rate.fetchone()
    obj_copy["metrics"] = "Action Success rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy
    