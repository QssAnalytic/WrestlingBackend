from sqlalchemy import text
from sqlalchemy.orm import Session

def takedown_success_rate(engine, params: dict):
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
        select *,round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) avg_takedowns
        from success s left join total t on s.fighter_id = t.fighter_id where s.fighter_id = :fighter_id
        """)
    with engine.connect() as conn:
        takedown_count = conn.execute(statement, params)
    return takedown_count.fetchone()

def takedown_per_match(engine, params: dict):
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
        group by f.fighter_id)
        select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match 
        from com c left join takedowns_count t on c.fighter = t.fighter_id where fighter= :fighter_id
        """)
    with engine.connect() as conn:
        takedown_per_match = conn.execute(statement, params)
    return takedown_per_match.fetchone()

def takedown_average_points_per_fight(engine, params: dict):
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
        takedowns_count as (select f.fighter_id, sum(score) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true 
        group by f.fighter_id)
        select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match 
        from com c left join takedowns_count t on c.fighter = t.fighter_id where c.fighter = :fighter_id
        """)
    with engine.connect() as conn:
        takedown_average_points_per_fight = conn.execute(statement, params)
    return takedown_average_points_per_fight.fetchone()
    
def takedown_count(engine, params: dict):
    statement = text("""
        select f.fighter_id, count(*) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id and f.successful = true and f2.fighter_id = :fighter_id  
        group by f.fighter_id
        """)
    with engine.connect() as conn:
        takedown_count = conn.execute(statement, params)
    return takedown_count.fetchone()

def single_leg_takedown_success_rate(engine, params:dict, db: Session):
    technique = db.query(engine.model).filter(engine.model.name == "Single leg takedown").first()   
    params['technique_id'] = technique.id
    statement = text("""
        with total as (
        select f.fighter_id, count(*) as total_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id --action_filter
        group by f.fighter_id 
        ),
        success as (
        select f.fighter_id, count(*) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true 
        group by f.fighter_id 
        )
        select s.fighter_id,round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) single_leg_success_rate
        from success s left join total t on s.fighter_id = t.fighter_id where s.fighter_id = :fighter_id
        """)
    with engine.connect() as conn:
        single_leg_takedown_success_rate = conn.execute(statement, params)
    return single_leg_takedown_success_rate.fetchone()

def single_leg_takedown_count(engine, params:dict, db: Session):
    technique = db.query(engine.model).filter(engine.model.name == "Single leg takedown").first()
    params['technique_id'] = technique.id
    statement = text("""
        select f.fighter_id, count(*) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true and f.fighter_id = :fighter_id
        group by f.fighter_id
        """)
    with engine.connect() as conn:
        single_leg_takedown_count = conn.execute(statement, params)
    return single_leg_takedown_count.fetchone()

def double_leg_takedown_count(engine, params:dict, db: Session):
    technique = db.query(engine.model).filter(engine.model.name == "Double leg takedown").first()
    
    params['technique_id'] = technique.id
    statement = text("""
        select f.fighter_id, count(*) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true and f.fighter_id = :fighter_id
        group by f.fighter_id
        """)
    with engine.connect() as conn:
        double_leg_takedown_count = conn.execute(statement, params)
    return double_leg_takedown_count.fetchone()


def double_leg_takedown_success_rate(engine, params:dict, db: Session):
    technique = db.query(engine.model).filter(engine.model.name == "Double leg takedown").first()   
    params['technique_id'] = technique.id
    statement = text("""
        with total as (
        select f.fighter_id, count(*) as total_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id --action_filter
        group by f.fighter_id 
        ),
        success as (
        select f.fighter_id, count(*) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.technique_id = :technique_id and f.successful = true 
        group by f.fighter_id 
        )
        select s.fighter_id,round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) single_leg_success_rate
        from success s left join total t on s.fighter_id = t.fighter_id where s.fighter_id = :fighter_id
        """)
    with engine.connect() as conn:
        double_leg_takedown_success_rate = conn.execute(statement, params)
    return double_leg_takedown_success_rate.fetchone()