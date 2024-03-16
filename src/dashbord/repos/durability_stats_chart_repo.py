from sqlalchemy import text
from sqlalchemy.orm import Session
from database import session_factory
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum
from src.app.models import ActionName, Technique


class DurabilityStatsChartRepo:

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