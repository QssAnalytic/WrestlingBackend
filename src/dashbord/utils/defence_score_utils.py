from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base
from src.app.models import ActionName
from src.dashbord.enums import DefenceStatsChartEnum
ModelTypeVar = TypeVar("ModelTypeVar", bound=Base)




def action_skipped_points_per_fight_utils(session_factory, params: dict, obj:dict, model, db: Session):
    obj_copy = obj.copy()
    obj_copy["star"] = True
    statement = text("""
        --Action skipped points per fight
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
                total_points as (select f.opponent_id, sum(score) as total_points from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                inner join actions a on f.action_name_id = a.id
                where extract(year from f2.fight_date) in :fight_date and f.successful = true
                group by f.opponent_id),
                calculation as(
                select fighter, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
                from com c left join total_points t on c.fighter = t.opponent_id)
        select * from (
        select *, round(cast(avg_points_per_match as decimal)/ cast(max(avg_points_per_match) over() as decimal), 2) from calculation
    ) where fighter = :fighter_id
""")
    with session_factory() as session:
        action_skipped_points_per_fight_rate = session.execute(statement, params)
        fetch = action_skipped_points_per_fight_rate.fetchone()
        # "Action skipped points per fight"
    obj_copy["metrics"] = DefenceStatsChartEnum.Action_skipped_points_per_fight
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy


def pin_to_parter_escape_rate_utils(session_factory, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    action = db.query(ActionName).filter(ActionName.name == "Pin to parter").first()
    params['action_name_id'] = action.id
    statement = text("""
        --pin to parterre escape rate
		WITH total AS (
		    SELECT 
		        f.opponent_id, 
		        COUNT(*) AS total_count 
		    FROM 
		        fightstatistics f
		    INNER JOIN 
		        fightinfos f2 ON f.fight_id = f2.id
		    WHERE 
		        EXTRACT(YEAR FROM f2.fight_date) IN :fight_date 
		        AND f.action_name_id = :action_name_id
		    GROUP BY 
		        f.opponent_id
		),
		success AS (
		    SELECT 
		        f.opponent_id, 
		        COUNT(*) AS successful_escape 
		    FROM 
		        fightstatistics f
		    INNER JOIN 
		        fightinfos f2 ON f.fight_id = f2.id
		    WHERE 
		        EXTRACT(YEAR FROM f2.fight_date) IN :fight_date 
		        AND f.successful = FALSE 
		        AND f.action_name_id = :action_name_id
		    GROUP BY 
		        f.opponent_id
		),
		calculation AS (
		    SELECT 
		        t.opponent_id,
		        ROUND(CAST(COALESCE(successful_escape, 0) AS DECIMAL), 2) AS succ,
		        ROUND(CAST(total_count AS DECIMAL), 2) AS tot,
		        ROUND(COALESCE(CAST(successful_escape AS DECIMAL), 0) / COALESCE(CAST(total_count AS DECIMAL), 1), 2) AS action_escape_rate
		    FROM 
		        total t 
		    LEFT JOIN 
		        success s ON s.opponent_id = t.opponent_id
		)  
		SELECT 
		    * 
		FROM 
		    (
		        SELECT 
		            opponent_id, 
		            action_escape_rate, 
		            succ, 
		            tot,
		            ROUND((action_escape_rate) / (MAX(action_escape_rate) OVER()), 2) AS bar_pct
		        FROM 
		            calculation
		    )  
		WHERE 
		    opponent_id = :fighter_id;
        """)
    with session_factory() as session:
        pin_to_parter_escape_rate = session.execute(statement, params)
        fetch = pin_to_parter_escape_rate.fetchone()
        # "Pin to parter escape rate"
    obj_copy["metrics"] = DefenceStatsChartEnum.Pin_to_parter_escape_rate
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["successful_count"] = fetch[2]
        obj_copy["total_count"] = fetch[3]
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy



def takedown_escape_rate_utils(session_factory, params: dict, obj: dict, db:Session):
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
	        select t.opponent_id,ROUND(CAST(s.successful_escape AS DECIMAL), 2) AS succ,
           ROUND(CAST(t.total_count AS DECIMAL), 2) AS tot,
	        round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id
            )  
        select * from (select opponent_id, action_escape_rate, succ,tot, 
                    round((action_escape_rate) /(max(action_escape_rate) over()), 2) bar_pct
                    from calculation)
        where opponent_id = :fighter_id
        """)
    with session_factory() as session:
        takedown_escape_rate = session.execute(statement, params)
        fetch = takedown_escape_rate.fetchone()
        # "Takedown escape rate"
    obj_copy["metrics"] = DefenceStatsChartEnum.Takedown_escape_rate
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy['successful_count'] = float(fetch[2])
        obj_copy['total_count'] = float(fetch[3])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy


def roll_escape_rate_utils(session_factory, params: dict, obj:dict, db: Session):
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
        select t.opponent_id,
        round(coalesce(cast(successful_escape as decimal), 0),2) as succ,
        round(coalesce(cast(total_count as decimal), 0),2) as tot,
        ROUND(COALESCE(CAST(successful_escape AS DECIMAL), 0) / CAST(total_count AS DECIMAL), 2) AS action_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id)  
        select * from (select opponent_id, action_escape_rate, succ, tot,
                    round(action_escape_rate /(max(action_escape_rate) over()), 2) bar_pct
                    from calculation) where opponent_id = :fighter_id
        """)
    with session_factory() as session:
        roll_escape_rate = session.execute(statement, params)
        fetch = roll_escape_rate.fetchone()
        # "Roll escape rate"
    obj_copy["metrics"] = DefenceStatsChartEnum.Roll_escape_rate
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy['successful_count'] = float(fetch[2])
        obj_copy['total_count'] = float(fetch[3])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy




def action_escape_rate_utils(session_factory, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    obj_copy["star"] = True
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
                    select t.opponent_id,round(cast(successful_escape as decimal),2) as succ, round(cast(total_count as decimal), 2) as tot,
                    round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
                        from total t left join success s on s.opponent_id = t.opponent_id)  
                    select * from (select opponent_id,action_escape_rate,succ,tot, 
                    round((action_escape_rate - min(action_escape_rate) over()) /(max(action_escape_rate) over() - min(action_escape_rate) over()), 2) bar_pct
                    from calculation)
            where opponent_id = :fighter_id
        """)
    with session_factory() as session:
        action_escape_rate = session.execute(statement, params)
        fetch = action_escape_rate.fetchone()
        # "Action escape rate"
    obj_copy["metrics"] = DefenceStatsChartEnum.Action_escape_rate
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["successful_count"] = float(fetch[2])
        obj_copy["total_count"] = float(fetch[3])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy

def protection_zone_escape_rate_utils(session_factory, params: dict,obj:dict, db: Session):
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
    with session_factory() as session:
        protection_zone_escape_rate = session.execute(statement, params)
        fetch = protection_zone_escape_rate.fetchone()
    obj_copy["metrics"] = "Protection zone escape rate"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["bar_pct"] = float(fetch[2])
    return obj_copy


def parterre_escape_rate_utils(session_factory, params: dict, model: ModelTypeVar, obj:dict,db: Session):
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
        select t.opponent_id,
        coalesce(successful_escape,0) as succ,
        coalesce(total_count,0) as tot,
        round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
            from total t left join success s on s.opponent_id = t.opponent_id)  
        select * from (select opponent_id, action_escape_rate, succ, tot,
                    round(action_escape_rate /(max(action_escape_rate) over()), 2) bar_pct
                    from calculation) where opponent_id = :fighter_id
        """)
    with session_factory() as session:
        parterre_escape_rate = session.execute(statement, params)

        fetch = parterre_escape_rate.fetchone()
# "Parterre escape rate"
    obj_copy["metrics"] = DefenceStatsChartEnum.Parterre_escape_rate
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
        obj_copy["successful_count"] = float(fetch[2])
        obj_copy["total_count"] = float(fetch[3])
        obj_copy["bar_pct"] = float(fetch[-1])
    return obj_copy
