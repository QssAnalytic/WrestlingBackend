from sqlalchemy import text
from sqlalchemy.orm import Session
from database import session_factory
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum
from src.app.models import ActionName, Technique


class DurabilityStatsChartRepo:

    @classmethod
    def offence_score_2nd_part(cls, params: dict, db:Session):
        statement = text("""
              --offense_score_durability
  with action_success_rate as(
        with total as (
                select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                
                where (((f2.order = 'ascending') and (f.action_time_second > 180)) 
						  or ((f2.order = 'descending') and (f.action_time_second < 180)))
                group by f.fighter_id, t_date
                ),
                success as (
                select f.fighter_id, count(*) as successful_count, extract(year from f2.fight_date) as s_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where f.successful = true  and (((f2.order = 'ascending') and (f.action_time_second > 180)) 
						  or ((f2.order = 'descending') and (f.action_time_second < 180)))
                group by f.fighter_id, s_date
                )
            select * from (    
            select fighter_id,action_success_rate_date, takedown_success_rate, successful_count, total_count,round((takedown_success_rate- 0) /(max(takedown_success_rate) over() - 0), 2) bar_pct from 
                (select t.fighter_id,coalesce(t.t_date,s.s_date) as action_success_rate_date, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
                from success s right join total t on s.fighter_id = t.fighter_id and t.t_date = s.s_date))
        ),
        --Action counts per fight
        action_count_per_fight as(
        with fighter_matches as (
        select s.fighter_id, array_agg(distinct fight_id) fighter_array, extract(year from i.fight_date) as fi_m_date from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            
            group by s.fighter_id, fi_m_date
        ),
        opponent_matches as (
        select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) op_m_date from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            
            group by s.opponent_id, op_m_date
        ),
        com as (select fighter,com_date, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
        select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_m_date,op.op_m_date) as com_date
        from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_m_date = op.op_m_date
        )),
        successful_action_attempts as (select f.fighter_id, count(*) as successful_attempts,  extract(year from f2.fight_date) as s_a_date from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where f.successful = true  and (((f2.order = 'ascending') and (f.action_time_second > 180)) 
						  or ((f2.order = 'descending') and (f.action_time_second < 180))) 
        group by f.fighter_id, s_a_date),
        total_action_attempts as (select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as t_a_date from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where (((f2.order = 'ascending') and (f.action_time_second > 180)) 
						  or ((f2.order = 'descending') and (f.action_time_second < 180)))
        group by f.fighter_id, t_a_date),
        calculation as(
        select fighter,c.com_date as action_count_per_fight_date, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_attempts_per_match,
        coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 1) as total_attempts_per_match
        from com c left join successful_action_attempts s on c.fighter = s.fighter_id and c.com_date = s.s_a_date
                left join total_action_attempts tc on c.fighter = tc.fighter_id and c.com_date = tc.t_a_date
        )
        select *, round(cast(successful_attempts_per_match as decimal)/ cast(max(successful_attempts_per_match) over() as decimal), 2) count_pct from calculation
        ),
        avg_points_per_fight as(
                with fighter_matches as (
                    select s.fighter_id, array_agg(distinct fight_id) fighter_array, extract(year from i.fight_date) as fi_m_date from fightstatistics s
                        inner join fightinfos i on s.fight_id = i.id
                        
                        group by s.fighter_id, fi_m_date
                    ),
                    opponent_matches as (
                    select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) as op_m_date from fightstatistics s
                        inner join fightinfos i on s.fight_id = i.id
                        
                        group by s.opponent_id, op_m_date 
                    ),
                    com as (select fighter,com_date, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
                    select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_m_date,op.op_m_date) as com_date
                    from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_m_date = op.op_m_date
                    )),
                    total_points as (select f.fighter_id, sum(score) as total_points, extract(year from f2.fight_date) as t_p_date from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    inner join actions a on f.action_name_id = a.id
                    where f.successful = true  and (((f2.order = 'ascending') and (f.action_time_second > 180)) 
						  or ((f2.order = 'descending') and (f.action_time_second < 180)))
                    group by f.fighter_id, t_p_date),
                    calculation as(
                    select fighter,c.com_date as avg_points_per_fight_date, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
                    from com c left join total_points t on c.fighter = t.fighter_id and c.com_date = t.t_p_date)
            select * from (
            select *, round(cast(avg_points_per_match as decimal)/ cast(max(avg_points_per_match) over() as decimal), 2) point_pct from calculation
        ))
        select fighter_id,f_date,  round(cast(bar_pct as decimal), 2),offense_score from (
        select *, percent_rank() over(order by offense_score asc) as bar_pct  from(
            select fighter_id,f_date,round(1 - cast(offense_rank as decimal) / cast(max(offense_rank) over() as decimal), 2) offense_score from(
            select *, rank() over(order by offense_pct desc) offense_rank from(
                select fighter_id,a.action_success_rate_date as f_date,(bar_pct + count_pct + point_pct) /3 offense_pct
        from action_success_rate a 
        left join action_count_per_fight c
        on a.fighter_id = c.fighter and a.action_success_rate_date = c.action_count_per_fight_date
        left join avg_points_per_fight p 
        on a.fighter_id = p.fighter and a.action_success_rate_date = p.avg_points_per_fight_date
            )))) where fighter_id = :fighter_id
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch


    @classmethod
    def defence_score_2nd_part(cls, params: dict, db:Session):
        statement = text("""
            --defense_score_durability
            with action_escape_rate as(
                with total as (
                        select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
                        inner join fightinfos f2 on f.fight_id = f2.id
                            where ((action_time_second > 180 and f2.order = 'ascending') or (action_time_second < 180 and f2.order = 'descending'))
                            group by f.opponent_id, t_date
                            ),
                            success as (
                            select f.opponent_id, count(*) as successful_escape, extract(year from f2.fight_date) as s_date from fightstatistics f
                            inner join fightinfos f2 on f.fight_id = f2.id
            
                            where f.successful = false and ( (action_time_second > 180 and f2.order = 'ascending') or  (action_time_second < 180 and f2.order = 'descending'))
                            group by f.opponent_id, s_date
                            ),
                
                calculation as (
                select t.opponent_id,t.t_date as cal_date, round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
                    from total t left join success s on s.opponent_id = t.opponent_id and t.t_date = s.s_date)  

            select * from (select opponent_id,cal_date as action_escape_rate_date, action_escape_rate,
                        round((action_escape_rate - min(action_escape_rate) over()) /(max(action_escape_rate) over() - min(action_escape_rate) over()), 2) bar_pct
                        from calculation)
            )
            select * from(
            select *, round(1 - cast(defense_rank as decimal) / cast(max(defense_rank) over() as decimal), 2) from(
            select *, rank() over(order by bar_pct desc) defense_rank from(
            select opponent_id, action_escape_rate_date, bar_pct from action_escape_rate))) where opponent_id = :fighter_id order by action_escape_rate_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def takedown_score_2nd_part(cls, params:dict, db:Session):
        action = db.query(ActionName).filter(ActionName.name == 'Takedown').first()
        params['action_name_id'] = action.id
        statement = text("""
        --takedown_durability_score
        with takedown_success as(
        with total as (
                select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                
                where  f.action_name_id = 1
                and
            ( (action_time_second > 180 and f2.order = 'ascending')
                or 
                (action_time_second < 180 and f2.order = 'descending'))
                group by f.fighter_id, t_date
                ),
                success as (
                select f.fighter_id, count(*) as successful_count, extract(year from f2.fight_date) as s_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where f.action_name_id = 1 and f.successful = true 
                    and
                    (
                    (action_time_second > 180 and f2.order = 'ascending')
                or 
                (action_time_second < 180 and f2.order = 'descending'))
                group by f.fighter_id, s_date
                )
            select * from (    
            select fighter_id, t_f_date, takedown_success_rate, successful_count, total_count,round((takedown_success_rate - min(takedown_success_rate) over()) /(max(takedown_success_rate) over() - min(takedown_success_rate) over()), 2) tkd_bar_pct from 
                (select t.fighter_id,t.t_date as t_f_date, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
                from success s right join total t on s.fighter_id = t.fighter_id and s.s_date = t.t_date))),
        avg_takedown_points_per_fight as(
        with fighter_matches as (
        select s.fighter_id, array_agg(distinct fight_id) fighter_array,extract(year from i.fight_date) as fi_m_date from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            
            group by s.fighter_id, fi_m_date
        ),
        opponent_matches as (
        select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) as op_m_date from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            
            group by s.opponent_id, op_m_date
        ),
        com as (select fighter, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches, com_date from (
        select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_m_date,op.op_m_date) as com_date
        from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_m_date = op.op_m_date
        )),
        takedowns_count as (select f.fighter_id, sum(score) as successful_count, extract(year from f2.fight_date) as t_c_date from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where f.action_name_id = :action_name_id and f.successful = true and
                            (
                            (action_time_second > 180 and f2.order = 'ascending')
                or 
                (action_time_second < 180 and f2.order = 'descending'))
        group by f.fighter_id, t_c_date),
        calculation as (
        select fighter,c.com_date as cal_date, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match
        from com c left join takedowns_count t on c.fighter = t.fighter_id and c.com_date = t.t_c_date)
        select * from (select fighter, tkd_per_match,
                    round((tkd_per_match - min(tkd_per_match) over()) /(max(tkd_per_match) over() - min(tkd_per_match) over()), 2) count_bar_pct, cal_date
                    from calculation)),
        takedown_per_fight_total as (
        with fighter_matches as (
                select s.fighter_id, array_agg(distinct fight_id) fighter_array,extract(year from i.fight_date) as fi_m_date from fightstatistics s
                    inner join fightinfos i on s.fight_id = i.id
                    
                    group by s.fighter_id, fi_m_date
                ),
                opponent_matches as (
                select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) as op_m_date from fightstatistics s
                    inner join fightinfos i on s.fight_id = i.id
                    
                    group by s.opponent_id, op_m_date
                ),
                com as (select fighter,com_date, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
                select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_m_date,op.op_m_date) as com_date
                from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_m_date = op.op_m_date
                )),
                takedowns_count as (select f.fighter_id, count(*) as successful_count, extract(year from f2.fight_date) as t_c_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where f.action_name_id = :action_name_id and f.successful = true 
                                    and (
                                    (action_time_second > 180 and f2.order = 'ascending')
                or 
                (action_time_second < 180 and f2.order = 'descending'))
                group by f.fighter_id, t_c_date),
                total as(
                select fighter,c.com_date as total_date, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match 
                from com c left join takedowns_count t on c.fighter = t.fighter_id and c.com_date = t.t_c_date)
                select * from (
                select *, round((tkd_per_match - 0) /(max(tkd_per_match) over() - 0), 2) bar_pct from total t) 
        )
            select fighter_id, f_date, score_pct from (
                select * from(
            select * from (
            select fighter_id, (tkd_bar_pct + bar_pct + count_bar_pct)/3 score_pct, t_f_date as f_date from takedown_success t
            left join avg_takedown_points_per_fight a
                on t.fighter_id = a.fighter and t.t_f_date = a.cal_date
            left join takedown_per_fight_total f 
            on t.fighter_id = f.fighter and t.t_f_date = f.total_date
        ))) where fighter_id = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch


    @classmethod
    def passivity_per_fight(cls, params:dict, db:Session):
        action = db.query(ActionName).filter(ActionName.name == 'Passivity').first()
        params['action_name_id'] = action.id
        statement = text("""
        --Passivity per fight
        with fighter_matches as (
        select s.fighter_id, array_agg(distinct fight_id) fighter_array,extract(year from i.fight_date) as fi_date from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            
            group by s.fighter_id, fi_date
        ),
        opponent_matches as (
        select s.opponent_id, array_agg(distinct fight_id) opponent_array,extract(year from i.fight_date) as op_date from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            
            group by s.opponent_id, op_date
        ),
        com as (select fighter, com_date, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
        select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_date,op.op_date) as com_date
        from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_date = op.op_date
        )),
        successful_action_attempts as (select f.fighter_id, count(*) as successful_attempts, extract(year from f2.fight_date) as s_a_date from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where f.successful = true and f.action_name_id = :action_name_id
        group by f.fighter_id, s_a_date),
        total_action_attempts as (select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as t_a_date from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        where f.action_name_id = :action_name_id
        group by f.fighter_id, t_a_date),
        calculation as(
        select fighter, c.com_date, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_attempts_per_match,
        coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) as total_attempts_per_match
        from com c left join successful_action_attempts s on c.fighter = s.fighter_id and c.com_date = s.s_a_date
                left join total_action_attempts tc on c.fighter = tc.fighter_id and c.com_date = tc.t_a_date
        )
        select * from calculation where fighter = :fighter_id order by com_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch
    @classmethod
    def total_action_counts_per_fight_2nd_part(cls, params:dict, db:Session):
        statement = text("""
                --total_late_attempts_per_fight
                with fighter_matches as (
                select s.fighter_id, array_agg(distinct fight_id) fighter_array,extract(year from i.fight_date) as fi_date from fightstatistics s
                    inner join fightinfos i on s.fight_id = i.id
                    
                    group by s.fighter_id , fi_date
                ),
                opponent_matches as (
                select s.opponent_id, array_agg(distinct fight_id) opponent_array,extract(year from i.fight_date) as op_date from fightstatistics s
                    inner join fightinfos i on s.fight_id = i.id
                    
                    group by s.opponent_id, op_date
                ),
                com as (select fighter,com_date, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
                select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_date,op.op_date) as com_date
                from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_date = op.op_date
                )),
                total_late_attempts as (select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as t_l_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                inner join actions a on f.action_name_id = a.id
                where  (((f2.order = 'ascending') and (f.action_time_second > 180)) 
                                        or ((f2.order = 'descending') and (f.action_time_second < 180)))
                group by f.fighter_id, t_l_date)
                select * from (
                select * from(
                select fighter,c.com_date as f_date, coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) 
                                as total_late_attempts_per_match
                from com c
                        left join total_late_attempts tc on c.fighter = tc.fighter_id and c.com_date = tc.t_l_date))
                where fighter = :fighter_id order by f_date
                
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def total_successful_defenses_per_fight_2nd_part(cls, params:dict, db:Session):
        statement = text("""
            --DURABILITY
            --total_late_defences_per_fight
            with fighter_matches as (
            select s.fighter_id, array_agg(distinct fight_id) fighter_array,extract(year from i.fight_date) as fi_date from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                
                group by s.fighter_id, fi_date
            ),
            opponent_matches as (
            select s.opponent_id, array_agg(distinct fight_id) opponent_array,extract(year from i.fight_date) as op_date from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                
                group by s.opponent_id, op_date
            ),
            com as (select fighter, com_date,cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
            select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_date,op.op_date) as com_date
            from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_date = op.op_date
            )),
            total_late_defences as (select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as t_l_d_date from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            where (((f2.order = 'ascending') and (f.action_time_second > 180)) 
                                    or ((f2.order = 'descending') and (f.action_time_second < 180)))
            group by f.opponent_id, t_l_d_date)
            select * from (
            select * from(
            select fighter,coalesce(c.com_date,tc.t_l_d_date) as f_date, coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) 
                            as total_late_defences_per_match
            from com c
                    left join total_late_defences tc on c.fighter = tc.opponent_id and c.com_date = tc.t_l_d_date)) 
            where fighter = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch