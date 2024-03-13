from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base, session_factory

ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)
def takedown_success_rate_utils(session_factory, params: dict, obj: dict):
    takedown_success_rate_string = "Takedown Success rate"
    obj_copy = obj.copy()
    statement = text("""
        with total as (
                select f.fighter_id, count(*) as total_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id
                group by f.fighter_id
                ),
                success as (
                select f.fighter_id, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
                group by f.fighter_id
                )
            select * from (    
            select fighter_id, takedown_success_rate, successful_count, total_count,round((takedown_success_rate - 0) /(max(takedown_success_rate) over() - 0), 2) bar_pct from 
                (select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
                from success s right join total t on s.fighter_id = t.fighter_id))
                where fighter_id = :fighter_id
        """)
    with session_factory() as session:
        takedown_count = session.execute(statement, params)
        fetch = takedown_count.fetchone()
    obj_copy["metrics"] = takedown_success_rate_string
    if fetch is not None:
        
        obj_copy["score"] = float(fetch[1])
        obj_copy["successful_count"] = fetch[2]
        obj_copy["total_count"] = fetch[3]
        obj_copy["bar_pct"] = float(fetch[4])
    return obj_copy

def takedown_per_match_utils(session_factory, params: dict, obj:dict):
    
    obj_copy = obj.copy()
    statement = text("""
        with fighter_matches as (
        select s.fighter_id, array_agg(distinct fight_id) fighter_array from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            where extract(year from i.fight_date) in :fight_date
            group by s.fighter_id 
        ),
        opponent_matches as (
        select s.opponent_id, array_agg(distinct fight_id) opponent_array from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            where extract(year from i.fight_date) in :fight_date
            group by s.opponent_id 
        ),
        com as (select fighter, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
        select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array 
        from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id
        )),
        takedowns_count as (select f.fighter_id, count(*) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
        group by f.fighter_id),
        total as(
        select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match 
        from com c left join takedowns_count t on c.fighter = t.fighter_id)
        select * from (
        select *, round((tkd_per_match - 0) /(max(tkd_per_match) over() - 0), 2) bar_pct from total t) 
        where fighter = :fighter_id
        """)
    with session_factory() as session:
        takedown_per_match = session.execute(statement, params)
        fetch = takedown_per_match.fetchone()
    if fetch != None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    obj_copy["metrics"] = "Takedown per fight total"
    return obj_copy

def takedown_average_points_per_fight_utils(session_factory, params: dict, obj: dict):
    obj_copy = obj.copy()
    statement = text("""
        --takedown average points per fight
        with fighter_matches as (
        select s.fighter_id, array_agg(distinct fight_id) fighter_array from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            where extract(year from i.fight_date) in :fight_date
            group by s.fighter_id 
        ),
        opponent_matches as (
        select s.opponent_id, array_agg(distinct fight_id) opponent_array from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            where extract(year from i.fight_date) in :fight_date
            group by s.opponent_id 
        ),
        com as (select fighter, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
        select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array 
        from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id
        )),
        takedowns_count as (select f.fighter_id, sum(score) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
        group by f.fighter_id),
        calculation as (
        select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match
        from com c left join takedowns_count t on c.fighter = t.fighter_id)
        select * from (select fighter, tkd_per_match,
                    round(cast((tkd_per_match - 0) as decimal) / cast((max(tkd_per_match) over() - 0) as decimal), 2) bar_pct
                    from calculation)
        where fighter = :fighter_id
        """)
    with session_factory() as session:
        takedown_average_points_per_fight = session.execute(statement, params)
        fetch = takedown_average_points_per_fight.fetchone()
    obj_copy["metrics"] = "Average takedown points per fight"
    if fetch is not None:
        
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy

    
def takedown_count_utils(session_factory, params: dict, obj: dict):
    obj_copy = obj.copy()
    statement = text("""
        with success as (select f.fighter_id, count(*) as successful_count from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
            group by f.fighter_id)
            select * from (
            select *, round(cast((successful_count - 0) as Decimal) /cast((max(successful_count) over() - 0) as Decimal), 2) bar_pct 
            from success) where fighter_id = :fighter_id
        """)
    with session_factory() as session:
        takedown_count = session.execute(statement, params)
        fetch = takedown_count.fetchone()
    obj_copy["metrics"] = "Takedown Count"
    if fetch is not None:
        
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy


def single_leg_takedown_success_rate_utils(session_factory, params:dict, model: ModelTypeVar, obj:dict, db: Session):
    technique = db.query(model).filter(model.name == "Single leg takedown").first()   
    params['technique_id'] = technique.id
    obj_copy = obj.copy()
    statement = text("""
        --single_leg_takedown_success_rate
        with total as (
                select f.fighter_id, count(*) as total_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id
                group by f.fighter_id
                ),
                success as (
                select f.fighter_id, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true 
                group by f.fighter_id
                )
            select * from (    
            select fighter_id, single_leg_takedown_success_rate, successful_count, total_count,round(cast((single_leg_takedown_success_rate - 0) as decimal) / cast((max(single_leg_takedown_success_rate) over() - 0) as decimal), 2) bar_pct from 
                (select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) single_leg_takedown_success_rate 
                from success s right join total t on s.fighter_id = t.fighter_id))
                where fighter_id = :fighter_id
        """)
    with session_factory() as session:
        single_leg_takedown_success_rate = session.execute(statement, params)
        fetch = single_leg_takedown_success_rate.fetchone()
    obj_copy["metrics"] = "Single Leg takedown Success Rate"
    if fetch is not None:
        obj_copy["successful_count"] = fetch[2]
        obj_copy["score"] = float(fetch[1])
        obj_copy["successful_count"] = fetch[2]
        obj_copy["total_count"] = fetch[3]
        obj_copy["bar_pct"] = float(fetch[4])
    return obj_copy


def single_leg_takedown_count_utils(session_factory, params:dict, model: ModelTypeVar, obj:dict, db: Session):
    technique = db.query(model).filter(model.name == "Single leg takedown").first()
    obj_copy = obj.copy()
    params['technique_id'] = technique.id
    statement = text("""
        with success as (select f.fighter_id, count(*) as successful_count from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true 
            group by f.fighter_id)
            select * from (
            select *, round(cast((successful_count - 0) as Decimal) /cast((max(successful_count) over() - 0) as Decimal), 2) bar_pct 
            from success) where fighter_id = :fighter_id
        """)
    with session_factory() as session:
        single_leg_takedown_count = session.execute(statement, params)
        fetch = single_leg_takedown_count.fetchone()

    obj_copy["metrics"] = "Single leg takedown count"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy

def double_leg_takedown_count_utils(session_factory, params:dict, model: ModelTypeVar, obj:dict, db: Session):
    technique = db.query(model).filter(model.name == "Double leg takedown").first()
    obj_copy = obj.copy()
    params['technique_id'] = technique.id
    statement = text("""
        with success as (select f.fighter_id, count(*) as successful_count from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true 
            group by f.fighter_id)
            select * from (
            select *, round(cast((successful_count - 0) as Decimal) /cast((max(successful_count) over() - 0) as Decimal), 2) bar_pct 
            from success) where fighter_id = :fighter_id
        """)
    with session_factory() as session:
        double_leg_takedown_count = session.execute(statement, params)
        fetch = double_leg_takedown_count.fetchone()
    obj_copy["metrics"] = "Double leg takedown counts"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy


def double_leg_takedown_success_rate_utils(session_factory, params:dict, model: ModelTypeVar, obj:dict, db: Session):
    obj_copy = obj.copy()
    technique = db.query(model).filter(model.name == "Double leg takedown").first()   
    params['technique_id'] = technique.id
    statement = text("""
        with total as (
                select f.fighter_id, count(*) as total_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id
                group by f.fighter_id
                ),
                success as (
                select f.fighter_id, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true 
                group by f.fighter_id
                )
            select * from (    
            select fighter_id, single_leg_takedown_success_rate, successful_count, total_count,round(cast((single_leg_takedown_success_rate - 0) as decimal) / cast((max(single_leg_takedown_success_rate) over() - 0) as decimal), 2) bar_pct from 
                (select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) single_leg_takedown_success_rate 
                from success s right join total t on s.fighter_id = t.fighter_id))
                where fighter_id = :fighter_id
        """)
    with session_factory() as session:
        double_leg_takedown_success_rate = session.execute(statement, params)

        fetch = double_leg_takedown_success_rate.fetchone()
    obj_copy["metrics"] = "Double Leg takedown Success Rate"
    if fetch is not None:
        obj_copy["successful_count"] = fetch[2]
        obj_copy["score"] = float(fetch[1])
        obj_copy["successful_count"] = fetch[2]
        obj_copy["total_count"] = fetch[3]
        obj_copy["bar_pct"] = float(fetch[4])
    return obj_copy
