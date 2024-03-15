from sqlalchemy import text
from sqlalchemy.orm import Session
from database import session_factory
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum
from src.app.models import ActionName, Technique


class OffenceStatsChartRepo:

    @classmethod
    def protection_zone_points_per_fight(cls, params:dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == 'Protection zone').first()
        params['action_name_id'] = action.id
        statement = text("""
            --protection_zone_points_per_fight
				with fighter_matches as (
            select s.fighter_id, array_agg(distinct fight_id) fighter_array,extract(year from i.fight_date) as fi_date from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                
                group by s.fighter_id, fi_date
            ),
            opponent_matches as (
            select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) as op_date from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                
                group by s.opponent_id, op_date
            ),
            com as (select fighter, com_date, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
            select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_date,op.op_date) as com_date
            from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_date = op.op_date
            )),
				total_points as (select f.fighter_id, sum(score) as total_points, extract(year from f2.fight_date) as t_date from fightstatistics f
				inner join fightinfos f2 on f.fight_id = f2.id
				where f.successful = true and f.action_name_id = :action_name_id
				group by f.fighter_id, t_date),
				calculation as(
				select fighter,coalesce(t.t_date,c.com_date) as cal_date, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
				from com c left join total_points t on c.fighter = t.fighter_id and t.t_date = c.com_date)
		select * from calculation where fighter = :fighter_id order by cal_date

        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def protection_zone_counts_per_fight(cls, params:dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == 'Protection zone').first()
        params['action_name_id'] = action.id
        statement = text("""
            --Protection zone counts per fight
            with fighter_matches as (
            select s.fighter_id, array_agg(distinct fight_id) fighter_array,extract(year from i.fight_date) as fi_date from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                
                group by s.fighter_id, fi_date
            ),
            opponent_matches as (
            select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) as op_date from fightstatistics s
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
            where  f.action_name_id = :action_name_id
            group by f.fighter_id, t_a_date),

            calculation as(
            select fighter,coalesce(c.com_date, s.s_a_date, tc.t_a_date) as cal_date, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_attempts_per_match,
            coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) as total_attempts_per_match
            from com c left join successful_action_attempts s on c.fighter = s.fighter_id and c.com_date = s.s_a_date
                    left join total_action_attempts tc on c.fighter = tc.fighter_id and c.com_date = tc.t_a_date
            )
            select * from calculation where fighter = :fighter_id
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch  

    @classmethod
    def protection_zone_success_rate(cls, params:dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == 'Protection zone').first()
        params['action_name_id'] = action.id
        statement = text("""
            --protection_zone_success_rate
            with total as (
                    select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    
                    where f.action_name_id = :action_name_id
                    group by f.fighter_id, t_date
                    ),
                    success as (
                    select f.fighter_id, count(*) as successful_count, extract(year from f2.fight_date) as s_date from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    where f.successful = true and f.action_name_id = :action_name_id
                    group by f.fighter_id,s_date
                    )
                select * from (    
                select fighter_id,f_date, successful_count, total_count,takedown_success_rate from 
                    (select t.fighter_id,coalesce(s.s_date,t.t_date) as f_date, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
                    from success s right join total t on s.fighter_id = t.fighter_id and s.s_date = t.t_date)) where fighter_id = :fighter_id
                
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch  
    

    @classmethod
    def action_point_per_fight(cls, params:dict, db: Session):
        statement = text("""

        --Action points per fight
        with fighter_matches as (
        select s.fighter_id, array_agg(distinct fight_id) fighter_array, extract(year from i.fight_date) as fi_date from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            
            group by s.fighter_id, fi_date
        ),
        opponent_matches as (
        select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) as op_date from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            
            group by s.opponent_id, op_date
        ),
        com as (select fighter, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches, com_date from (
        select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(fi.fi_date, op.op_date) as com_date
        from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_date = op.op_date
        )),
        total_points as (select f.fighter_id, sum(score) as total_points, extract(year from f2.fight_date) as t_date from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
          and f.successful = true
        group by f.fighter_id, t_date),
        calculation as(
        select fighter,coalesce( c.com_date,t.t_date) as cal_date, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
        from com c left join total_points t on c.fighter = t.fighter_id and c.com_date = t.t_date)
            select * from calculation where fighter = :fighter_id
 		
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch  

    @classmethod
    def action_counts_per_fight(cls, params:dict, db:Session):
        statement = text("""
            --Action counts per fight
            with fighter_matches as (
            select s.fighter_id, array_agg(distinct fight_id) fighter_array, extract(year from i.fight_date) as fi_date from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                
                group by s.fighter_id, fi_date
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
            successful_action_attempts as (select f.fighter_id, count(*) as successful_attempts, extract(year from f2.fight_date) as s_a_date from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            where f.successful = true 
            group by f.fighter_id, s_a_date),
            total_action_attempts as (select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as t_a_date from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            group by f.fighter_id, t_a_date),
            calculation as(
            select fighter,coalesce(c.com_date, s.s_a_date,tc.t_a_date) as cal_date, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_attempts_per_match,
            coalesce(round(cast(total_count as decimal)/cast(unique_matches as decimal), 2), 0) as total_attempts_per_match
            from com c left join successful_action_attempts s on c.fighter = s.fighter_id and c.com_date = s.s_a_date
                    left join total_action_attempts tc on c.fighter = tc.fighter_id and c.com_date = tc.t_a_date
            )
            select * from (select *, round(cast(successful_attempts_per_match as decimal)/ cast(max(successful_attempts_per_match) over() as decimal), 2) from calculation)
            where fighter = :fighter_id order by cal_date
 		
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def action_success_rate(cls, params:dict, db:Session):
        statement = text("""
            --action_success_rate
            with total as (
                    select f.fighter_id, count(*) as total_count,extract(year from f2.fight_date) as t_date from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    
                    
                    group by f.fighter_id, t_date
                    ),
                    success as (
                    select f.fighter_id, count(*) as successful_count, extract(year from f2.fight_date) as s_date from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    where f.successful = true 
                    group by f.fighter_id, s_date
                    )
                select * from (    
                select fighter_id, f_date, takedown_success_rate, successful_count, total_count,round((takedown_success_rate- 0) /(max(takedown_success_rate) over() - 0), 2) bar_pct from 
                    (select t.fighter_id,coalesce(t.t_date, s.s_date) as f_date ,coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 1), 2) takedown_success_rate
                    from success s right join total t on s.fighter_id = t.fighter_id and t.t_date = s.s_date))
                where fighter_id = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch