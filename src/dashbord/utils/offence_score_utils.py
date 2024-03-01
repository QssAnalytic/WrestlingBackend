from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base
from src.app.models import ActionName


def parterre_success_rate_utils(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
--parterre_success_rate
	with total as (
			select f.fighter_id, count(*) as total_count from fightstatistics f
			inner join fightinfos f2 on f.fight_id = f2.id

			where extract(year from f2.fight_date) in :fight_date and  f.technique_id in (26, 29, 30, 38, 40)
			group by f.fighter_id
			),
			success as (
			select f.fighter_id, count(*) as successful_count from fightstatistics f
			inner join fightinfos f2 on f.fight_id = f2.id
			where extract(year from f2.fight_date) in :fight_date and f.successful = true and  f.technique_id in (26, 29, 30, 38, 40)
			group by f.fighter_id
			)
		select * from (    
		select fighter_id, takedown_success_rate, successful_count, total_count,round((takedown_success_rate- 0) /(max(takedown_success_rate) over() - 0), 2) bar_pct from 
			(select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
			from success s right join total t on s.fighter_id = t.fighter_id)) where fighter_id = :fighter_id
        """)
    with engine.connect() as conn:
        parterre_success_rate_utils = conn.execute(statement, params)
    fetch = parterre_success_rate_utils.fetchone()

    obj_copy["metrics"] = "Parterre success rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy


def roll_points_per_fight_utils(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
--Roll points per fight
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
				total_points as (select f.fighter_id, sum(score) as total_points from fightstatistics f
				inner join fightinfos f2 on f.fight_id = f2.id
				inner join actions a on f.action_name_id = a.id
				where extract(year from f2.fight_date) in :fight_date  and f.successful = true and f.action_name_id = 2
				group by f.fighter_id),
				calculation as(
				select fighter, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
				from com c left join total_points t on c.fighter = t.fighter_id)
		select * from (
		select *, round(cast(avg_points_per_match as decimal)/ cast(max(avg_points_per_match) over() as decimal), 2) from calculation
	) where fighter = :fighter_id
        """)
    with engine.connect() as conn:
        roll_count_per_fight_rate = conn.execute(statement, params)
    fetch = roll_count_per_fight_rate.fetchone()

    obj_copy["metrics"] = "Roll points per fight"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy



def roll_count_per_fight_utils(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
        --Roll counts per fight
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
        successful_action_attempts as (select f.fighter_id, count(*) as successful_attempts from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date  and f.successful = true and f.action_name_id = 2
        group by f.fighter_id),
        total_action_attempts as (select f.fighter_id, count(*) as total_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = 2
        group by f.fighter_id),

        calculation as(
        select fighter, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_attempts_per_match,
        coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) as total_attempts_per_match
        from com c left join successful_action_attempts t on c.fighter = t.fighter_id
                left join total_action_attempts tc on c.fighter = tc.fighter_id
        )
        select * from (
            select *, round(cast(successful_attempts_per_match as decimal)/ cast(max(successful_attempts_per_match) over() as decimal), 2) from calculation
        ) where fighter = :fighter_id

        """)
    with engine.connect() as conn:
        roll_count_per_fight = conn.execute(statement, params)
    fetch = roll_count_per_fight.fetchone()

    obj_copy["metrics"] = "Roll count per fight"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy

def roll_success_rate_utils(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
with total as (
        select f.fighter_id, count(*) as total_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = 2
        group by f.fighter_id
        ),
        success as (
        select f.fighter_id, count(*) as successful_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where extract(year from f2.fight_date) in :fight_date and f.successful = true and f.action_name_id = 2
        group by f.fighter_id
        )
    select * from (    
	select fighter_id, takedown_success_rate, successful_count, total_count,round((takedown_success_rate- 0) /(max(takedown_success_rate) over() - 0), 2) bar_pct from 
		(select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
        from success s right join total t on s.fighter_id = t.fighter_id)) where fighter_id = :fighter_id

        """)
    with engine.connect() as conn:
        roll_success_rate = conn.execute(statement, params)
    fetch = roll_success_rate.fetchone()

    obj_copy["metrics"] = "Roll success rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy

def protection_zone_points_per_fight_utils(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
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
				total_points as (select f.fighter_id, sum(score) as total_points from fightstatistics f
				inner join fightinfos f2 on f.fight_id = f2.id
				inner join actions a on f.action_name_id = a.id
				where extract(year from f2.fight_date) in :fight_date  and f.successful = true and f.action_name_id = 4
				group by f.fighter_id),
				calculation as(
				select fighter, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
				from com c left join total_points t on c.fighter = t.fighter_id)
		select * from (
		select *, round(cast(avg_points_per_match as decimal)/ cast(max(avg_points_per_match) over() as decimal), 2) from calculation
	) where fighter = :fighter_id

        """)
    with engine.connect() as conn:
        protection_zone_points_per_fight = conn.execute(statement, params)
    fetch = protection_zone_points_per_fight.fetchone()

    obj_copy["metrics"] = "Protection zone points per fight"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy

def offence_protection_count_per_fight(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
        --Protection zone counts per fight
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
        successful_action_attempts as (select f.fighter_id, count(*) as successful_attempts from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date  and f.successful = true and f.action_name_id = 4
        group by f.fighter_id),
        total_action_attempts as (select f.fighter_id, count(*) as total_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = 4
        group by f.fighter_id),

        calculation as(
        select fighter, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_attempts_per_match,
        coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) as total_attempts_per_match
        from com c left join successful_action_attempts t on c.fighter = t.fighter_id
                left join total_action_attempts tc on c.fighter = tc.fighter_id
        )
        select * from (
            select *, round(cast(successful_attempts_per_match as decimal)/ cast(max(successful_attempts_per_match) over() as decimal), 2) from calculation
        ) where fighter = :fighter_id

        """)
    with engine.connect() as conn:
        offence_protection_count_per_fight = conn.execute(statement, params)
    fetch = offence_protection_count_per_fight.fetchone()

    obj_copy["metrics"] = "Protection zone count per fight"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy

def offence_protection_zone_success_rate(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
    --protection_zone_success_rate
    with total as (
            select f.fighter_id, count(*) as total_count from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            
            where extract(year from f2.fight_date) in :fight_date and f.action_name_id = 4
            group by f.fighter_id
            ),
            success as (
            select f.fighter_id, count(*) as successful_count from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            where extract(year from f2.fight_date) in :fight_date and f.successful = true and f.action_name_id = 4
            group by f.fighter_id
            )
        select * from (    
        select fighter_id, takedown_success_rate, successful_count, total_count,round((takedown_success_rate- 0) /(max(takedown_success_rate) over() - 0), 2) bar_pct from 
            (select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
            from success s right join total t on s.fighter_id = t.fighter_id)) where fighter_id = :fighter_id

        """)
    with engine.connect() as conn:
        offence_protection_zone_success_rate = conn.execute(statement, params)
    fetch = offence_protection_zone_success_rate.fetchone()

    obj_copy["metrics"] = "Protection zone success rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy


def offence_action_success_rate_utils(engine, params: dict, obj:dict, db: Session):
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
            where fighter_id = :fighter_id
        """)
    with engine.connect() as conn:
        action_success_rate = conn.execute(statement, params)
    fetch = action_success_rate.fetchone()

    obj_copy["metrics"] = "Action Success rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[4])
    return obj_copy


def offence_action_point_per_fight(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
        --Action points per fight
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
        total_points as (select f.fighter_id, sum(score) as total_points from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date  and f.successful = true
        group by f.fighter_id),
        calculation as(
        select fighter, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
        from com c left join total_points t on c.fighter = t.fighter_id)
            select * from (
            select *, round(cast(avg_points_per_match as decimal)/ cast(max(avg_points_per_match) over() as decimal), 2) from calculation
        ) where fighter = :fighter_id
        """)
    with engine.connect() as conn:
        offence_action_point_per_fight = conn.execute(statement, params)
    fetch = offence_action_point_per_fight.fetchone()
    obj_copy["metrics"] = "Action points per fight"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])

        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy


def offence_action_count_per_fight(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    """"""
    statement = text("""
        --Action counts per fight
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
        successful_action_attempts as (select f.fighter_id, count(*) as successful_attempts from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date  and f.successful = true 
        group by f.fighter_id),
        total_action_attempts as (select f.fighter_id, count(*) as total_count from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where extract(year from f2.fight_date) in :fight_date
        group by f.fighter_id),
        calculation as(
        select fighter, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_attempts_per_match,
        coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) as total_attempts_per_match
        from com c left join successful_action_attempts t on c.fighter = t.fighter_id
                left join total_action_attempts tc on c.fighter = tc.fighter_id
        )
        select * from (select *, round(cast(successful_attempts_per_match as decimal)/ cast(max(successful_attempts_per_match) over() as decimal), 2) from calculation) where fighter = :fighter_id
        """)
    with engine.connect() as conn:
        action_count_per_fight = conn.execute(statement, params)
    fetch = action_count_per_fight.fetchone()
    obj_copy["metrics"] = "Action count per fight"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["total_count"] =float(fetch[2])
        obj_copy["bar_pct"] = float(fetch[3])
    return obj_copy