from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base
from src.app.models import ActionName

ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)

def pin_to_parter_escape_rate_utils(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    action = db.query(ActionName).filter(ActionName.name == "Pin to parter").first()
    params['action_name_id'] = action.id
    statement = text("""
        --pin to parterre escape rate
        with total as (
                    select f.opponent_id, count(*) as total_count from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                        
                        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id
                        group by f.opponent_id
                        ),
                        success as (
                        select f.opponent_id, count(*) as successful_escape from fightstatistics f
                        inner join fightinfos f2 on f.fight_id = f2.id
        
                        where extract(year from f2.fight_date) in :fight_date and f.successful = false and f.action_name_id = :action_name_id
                        group by f.opponent_id
                        ),
            
        calculation as (
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id)  

        select * from (select opponent_id, action_escape_rate,
                    round((action_escape_rate) /(max(action_escape_rate) over()), 2) bar_pct
                    from calculation)  where opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        pin_to_parter_escape_rate = conn.execute(statement, params)
    fetch = pin_to_parter_escape_rate.fetchone()
    obj_copy["metrics"] = "Pin to parter escape rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy



def takedown_escape_rate_utils(engine, params: dict, obj: dict, db:Session):
    obj_copy = obj.copy()
    action = db.query(ActionName).filter(ActionName.name == "Takedown").first()
    params['action_name_id'] = action.id
    statement = text("""
        --takedown escape rate
        with total as (
                    select f.opponent_id, count(*) as total_count from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                        
                        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id
                        group by f.opponent_id
                        ),
                        success as (
                        select f.opponent_id, count(*) as successful_escape from fightstatistics f
                        inner join fightinfos f2 on f.fight_id = f2.id
        
                        where extract(year from f2.fight_date) in :fight_date and f.successful = false and f.action_name_id = :action_name_id
                        group by f.opponent_id
                        ),
        calculation as (
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id)  

        select * from (select opponent_id, action_escape_rate,
                    round((action_escape_rate) /(max(action_escape_rate) over()), 2) bar_pct
                    from calculation)
        where opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        takedown_escape_rate = conn.execute(statement, params)
    fetch = takedown_escape_rate.fetchone()
    obj_copy["metrics"] = "Takedown escape rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy


def roll_escape_rate_utils(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
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
        
                        where extract(year from f2.fight_date) in :fight_date and f.successful = false and f.action_name_id = :action_name_id
                        group by f.opponent_id
                        ),    
        calculation as (
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id)  
        select * from (select opponent_id, action_escape_rate,
                    round(action_escape_rate /(max(action_escape_rate) over()), 2) bar_pct
                    from calculation) where opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        roll_escape_rate = conn.execute(statement, params)
    fetch = roll_escape_rate.fetchone()
    obj_copy["metrics"] = "Roll escape rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy




def action_escape_rate_utils(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
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
                                    ),
                    calculation as (
                    select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
                        from total t left join success s on s.opponent_id = t.opponent_id)  
                    select * from (select opponent_id, action_escape_rate,
                    round((action_escape_rate - min(action_escape_rate) over()) /(max(action_escape_rate) over() - min(action_escape_rate) over()), 2) bar_pct
                    from calculation)
            where opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        action_escape_rate = conn.execute(statement, params)
    fetch = action_escape_rate.fetchone()
    obj_copy["metrics"] = "Action escape rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy

def protection_zone_escape_rate_utils(engine, params: dict,obj:dict, db: Session):
    obj_copy = obj.copy()
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
        
                        where extract(year from f2.fight_date) in :fight_date and f.successful = false and f.action_name_id = :action_name_id
                        group by f.opponent_id
                        ),    
        calculation as (
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id)  
        select * from (select opponent_id, action_escape_rate,
                    round(action_escape_rate /(max(action_escape_rate) over()), 2) bar_pct
                    from calculation) where opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        protection_zone_escape_rate = conn.execute(statement, params)
    fetch = protection_zone_escape_rate.fetchone()
    obj_copy["metrics"] = "Protection zone escape rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy


def parterre_escape_rate_utils(engine, params: dict, model: ModelTypeVar, obj:dict,db: Session):
    technique_names = ['Leg lace', 'Roll from parter', 'Arm-lock roll on parter', 'Gator roll', 'Pin to parter']
    obj_copy = obj.copy()
    result = db.query(model.id).filter(model.name.in_(technique_names)).all()
    technique_ids = tuple((row[0] for row in result))
    params['technique_id'] = technique_ids
    statement = text("""
        --parterre escape rate
        with total as (
                    select f.opponent_id, count(*) as total_count from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                        
                        where extract(year from f2.fight_date) in :fight_date and f.technique_id in :technique_id
                        group by f.opponent_id
                        ),
                        success as (
                        select f.opponent_id, count(*) as successful_escape from fightstatistics f
                        inner join fightinfos f2 on f.fight_id = f2.id
        
                        where extract(year from f2.fight_date) in :fight_date and f.successful = false and f.technique_id in :technique_id
                        group by f.opponent_id
                        ),
            
        calculation as (
        select t.opponent_id,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id)  

        select * from (select opponent_id, action_escape_rate,
                    round(action_escape_rate /(max(action_escape_rate) over()), 2) bar_pct
                    from calculation) where opponent_id = :fighter_id
        """)
    with engine.connect() as conn:
        parterre_escape_rate = conn.execute(statement, params)

    fetch = parterre_escape_rate.fetchone()

    obj_copy["metrics"] = "Parterre escape rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy
