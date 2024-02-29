from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base
from src.app.models import ActionName

ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)

def pin_to_parter_escape_rate_utils(engine, params: dict, db: Session):
    action = db.query(ActionName).filter(ActionName.name == "Pin to parter").first()
    params['action_name_id'] = action.id
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


def takedown_escape_rate_utils(engine, params: dict, db:Session):
    action = db.query(ActionName).filter(ActionName.name == "Takedown").first()
    params['action_name_id'] = action.id
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


def roll_escape_rate_utils(engine, params: dict, db: Session):
    action = db.query(ActionName).filter(ActionName.name == "Roll").first()
    params['action_name_id'] = action.id
    statement = text("""
        --roll escape rate
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
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) roll_escape_rate
        from total t left join success s on s.opponent_id = t.opponent_id where t.opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        roll_escape_rate = conn.execute(statement, params)
    return roll_escape_rate.fetchone()



def action_escape_rate_utils(engine, params: dict, db: Session):
    # action = db.query(ActionName).filter(ActionName.name == "Roll").first()
    # params['action_name_id'] = action.id
    statement = text("""
        --action escape rate
        with total as (
            select f.opponent_id, count(*) as total_count from fightstatistics f
          	inner join fightinfos f2 on f.fight_id = f2.id
                
                where extract(year from f2.fight_date) in :fight_date
                group by f.opponent_id
                ),
                success as (
                select f.opponent_id, count(*) as successful_escape from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
   
                where extract(year from f2.fight_date) in :fight_date and f.successful = false 
                group by f.opponent_id
                )
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
        from total t left join success s on s.opponent_id = t.opponent_id where t.opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        action_escape_rate = conn.execute(statement, params)
    return action_escape_rate.fetchone()

def protection_zone_escape_rate_utils(engine, params: dict, db: Session):
    action = db.query(ActionName).filter(ActionName.name == "Protection zone").first()
    params['action_name_id'] = action.id
    statement = text("""
        --protection_zone_escape_rate
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
            select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) protection_zone_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id where t.opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        protection_zone_escape_rate = conn.execute(statement, params)
    return protection_zone_escape_rate.fetchone()

def parterre_escape_rate_utils(engine, params: dict, model: ModelTypeVar ,db: Session):
    technique_names = ['Leg lace', 'Out of from passivity zone', 'Arm-lock roll on parter', 'Gator roll', 'Pin to parter']

    result = db.query(model.id).filter(model.name.in_(technique_names)).all()
    technique_ids = tuple((row[0] for row in result))
    params['technique_ids'] = technique_ids
    statement = text("""
        --parterre_escape_rate
        with total as (
            select f.opponent_id, count(*) as total_count from fightstatistics f
          	inner join fightinfos f2 on f.fight_id = f2.id
                
                where extract(year from f2.fight_date) in :fight_date and f.technique_id in :technique_ids

                group by f.opponent_id
                ),
                success as (
                select f.opponent_id, count(*) as successful_escape from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
   
                where extract(year from f2.fight_date) in :fight_date and f.technique_id in :technique_ids and f.successful = false 
                group by f.opponent_id
                )
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) parterre_escape_rate
        from total t left join success s on s.opponent_id = t.opponent_id
        """)
    with engine.connect() as conn:
        parterre_escape_rate = conn.execute(statement, params)
    return parterre_escape_rate.fetchone()