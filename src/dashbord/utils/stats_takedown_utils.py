from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base
from src.app.models import ActionName
from src.dashbord.utils.durability_score_utils import takedown_durability_score_utils,  defence_durability_score_utils, offence_durability_score_utils

def stats_takedown(session_factory, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    statement = text("""
        --takedown_score stats
        with takedown_success as(
        with total as (
                select f.fighter_id, count(*) as total_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = 1
                group by f.fighter_id
                ),
                success as (
                select f.fighter_id, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = 1 and f.successful = true 
                group by f.fighter_id
                )
            select * from (    
            select fighter_id, takedown_success_rate, successful_count, total_count,round((takedown_success_rate - min(takedown_success_rate) over()) /(max(takedown_success_rate) over() - min(takedown_success_rate) over()), 2) tkd_bar_pct from 
                (select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
                from success s right join total t on s.fighter_id = t.fighter_id))),
        avg_takedown_points_per_fight as(
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
        where extract(year from f2.fight_date) in :fight_date and f.action_name_id = 1 and f.successful = true 
        group by f.fighter_id),

        calculation as (
        select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match
        from com c left join takedowns_count t on c.fighter = t.fighter_id)

        select * from (select fighter, tkd_per_match,
                    round((tkd_per_match - min(tkd_per_match) over()) /(max(tkd_per_match) over() - min(tkd_per_match) over()), 2) count_bar_pct
                    from calculation)),
        takedown_per_fight_total as (
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
                where extract(year from f2.fight_date) in :fight_date and f.action_name_id = 1 and f.successful = true 
                group by f.fighter_id),
                total as(
                select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match 
                from com c left join takedowns_count t on c.fighter = t.fighter_id)
                select * from (
                select *, round((tkd_per_match - 0) /(max(tkd_per_match) over() - 0), 2) bar_pct from total t) 
        )
            select * from (
                select *, round(1 - cast(tkd_rank as decimal) / cast(max(tkd_rank) over() as decimal), 2) from(
            select *, rank() over(order by score_pct desc) tkd_rank from (
            select fighter_id, (tkd_bar_pct + bar_pct + count_bar_pct)/3 score_pct from takedown_success t
            left join avg_takedown_points_per_fight a
                on t.fighter_id = a.fighter
            left join takedown_per_fight_total f
            on t.fighter_id = f.fighter
        ))) where fighter_id = :fighter_id

""")
    with session_factory() as session:
        stats_takedown = session.execute(statement, params)
        fetch = stats_takedown.fetchone()

    obj_copy["metrics"] = "Takedown Score"
    if fetch is not None:
        obj_copy["score"] = float(fetch[-1])
    return obj_copy


def stats_defence(session_factory, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    statement = text("""
        --defense_score
        with action_escape_rate as(
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
        )
        select * from(
        select *, round(1 - cast(defense_rank as decimal) / cast(max(defense_rank) over() as decimal), 2) from(
        select *, rank() over(order by bar_pct desc) defense_rank from(
        select opponent_id, bar_pct from action_escape_rate))) where opponent_id = :fighter_id

""")
    with session_factory() as session:
        stats_defence = session.execute(statement, params)
        fetch = stats_defence.fetchone()

    obj_copy["metrics"] = "Defence Score"
    if fetch is not None:
        obj_copy["score"] = float(fetch[-1])
    return obj_copy


def stats_offence(session_factory, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    statement = text("""
        --offense_score
        with action_success_rate as(
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
                (select t.fighter_id, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
                from success s right join total t on s.fighter_id = t.fighter_id))
            
        ),
        --Action counts per fight
        action_count_per_fight as(
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
        coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 1) as total_attempts_per_match
        from com c left join successful_action_attempts t on c.fighter = t.fighter_id
                left join total_action_attempts tc on c.fighter = tc.fighter_id
        )
        select *, round(cast(successful_attempts_per_match as decimal)/ cast(max(successful_attempts_per_match) over() as decimal), 2) count_pct from calculation),

        avg_points_per_fight as(
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
            select *, round(cast(avg_points_per_match as decimal)/ cast(max(avg_points_per_match) over() as decimal), 2) point_pct from calculation
        ))
        select * from (
            select fighter_id, round(1 - cast(offense_rank as decimal) / cast(max(offense_rank) over() as decimal), 2) offense_score from(
            select *, rank() over(order by offense_pct desc) offense_rank from(
                select fighter_id, (bar_pct + count_pct + point_pct) /3 offense_pct
        from action_success_rate a 
        left join action_count_per_fight c
        on a.fighter_id = c.fighter
        left join avg_points_per_fight p
        on a.fighter_id = p.fighter
            ))) where fighter_id = :fighter_id
""")
    with session_factory() as conn:
        stats_defence = conn.execute(statement, params)
        fetch = stats_defence.fetchone()

    obj_copy["metrics"] = "Offence Score"
    if fetch is not None:
        obj_copy["score"] = float(fetch[-1])
    return obj_copy

def stats_durability(session_factory, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()
    action = db.query(ActionName).filter(ActionName.name == "Passivity").first()
    params['action_name_id'] = action.id
    statement = text("""
        --DURABILITY_SCORE
            with passivity_per_fight as (
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
            where extract(year from f2.fight_date) in :fight_date  and f.successful = true and f.action_name_id = :action_name_id
            group by f.fighter_id),
            total_action_attempts as (select f.fighter_id, count(*) as total_count from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            where extract(year from f2.fight_date) in :fight_date and f.action_name_id = :action_name_id
            group by f.fighter_id),

            calculation as(
            select fighter, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_attempts_per_match,
            coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) as total_attempts_per_match
            from com c left join successful_action_attempts t on c.fighter = t.fighter_id
                    left join total_action_attempts tc on c.fighter = tc.fighter_id
            )
            select * from (
                select *, round(cast(successful_attempts_per_match as decimal)/ cast(max(successful_attempts_per_match) over() as decimal), 2) passivity_rank from calculation
            ) order by passivity_rank desc
            ),
            late_defences_per_fight as (
            --DURABILITY
            --total_late_defences_per_fight
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
            total_late_defences as (select f.opponent_id, count(*) as total_count from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            where extract(year from f2.fight_date) in :fight_date  and (((f2.order = 'ascending') and (f.action_time_second > 180)) 
                                    or ((f2.order = 'descending') and (f.action_time_second < 180)))
            group by f.opponent_id)
            select * from (
            select *, round(cast (percent_rank() over(order by total_late_defences_per_match asc) as decimal), 2) defense_rank from(
            select fighter, coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) 
                            as total_late_defences_per_match
            from com c
                    left join total_late_defences tc on c.fighter = tc.opponent_id)) 
            ),
            late_attempts_per_fight as (
            --DURABILITY
            --total_late_attempts_per_fight
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
            total_late_attempts as (select f.fighter_id, count(*) as total_count from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            where extract(year from f2.fight_date) in :fight_date  and (((f2.order = 'ascending') and (f.action_time_second > 180)) 
                                    or ((f2.order = 'descending') and (f.action_time_second < 180)))
            group by f.fighter_id)
            select * from (
            select *, round(cast (percent_rank() over(order by total_late_attempts_per_match asc) as decimal), 2) offense_rank from(
            select fighter, coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) 
                            as total_late_attempts_per_match
            from com c
                    left join total_late_attempts tc on c.fighter = tc.fighter_id))
            ),
            calculation as(
            select coalesce(p.fighter, d.fighter, a.fighter) fighter, cast(((passivity_rank + defense_rank + offense_rank) /3) as decimal) durability_score from passivity_per_fight p
            full outer join late_defences_per_fight d on p.fighter = d.fighter
            full outer join late_attempts_per_fight a on p.fighter = a.fighter)
            select fighter, round(durability_score, 2) as durability_score, round(cast(percent_rank() over(order by durability_score asc) as decimal), 2) as percent from calculation where fighter = :fighter_id

    """)
    with session_factory() as conn:
        stats_defence = conn.execute(statement, params)
        fetch = stats_defence.fetchone()
    obj_copy["metrics"] = "Durability Score"
    if fetch is not None:
        obj_copy["score"] = float(fetch[1])
    return obj_copy