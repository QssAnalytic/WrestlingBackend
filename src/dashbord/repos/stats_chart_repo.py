from sqlalchemy import text
from sqlalchemy.orm import Session
from database import session_factory
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum
from src.app.models import ActionName, Technique
class StatsChartRepo:


    @classmethod
    def doible_leg_takedown_success_rate(cls, params: dict, db: Session):
        technique = db.query(Technique).filter(Technique.name == "Double leg takedown").first()
        params['technique_id'] = technique.id
        statement = text("""
            ---singe_leg_takedown_success_rate_by_year
                with total as (
                        select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as tot_date from fightstatistics f
                        inner join fightinfos f2 on f.fight_id = f2.id
                        
                        where  f.technique_id = :technique_id
                        group by f.fighter_id, tot_date
                        ),
                        success as (
                        select f.fighter_id, count(*) as successful_count, extract(year from f2.fight_date) as suc_date from fightstatistics f
                        inner join fightinfos f2 on f.fight_id = f2.id
                        where  f.technique_id = :technique_id and f.successful = true 
                        group by f.fighter_id, suc_date
                        )
                    select * from (    
                    
                        (select t.fighter_id,coalesce (s.suc_date, t.tot_date) as f_date, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) single_leg_takedown_success_rate
                        from success s right join total t on s.fighter_id = t.fighter_id and s.suc_date = t.tot_date)) where fighter_id = :fighter_id order by f_date	
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch


    @classmethod
    def double_leg_takedown_count(cls, params: dict, db: Session):
        technique = db.query(Technique).filter(Technique.name == "Double leg takedown").first()
        params['technique_id'] = technique.id
        statement = text("""
            ---doube_leg_takedown_count_by_year
            with success as (select f.fighter_id,extract(year from f2.fight_date) as s_date, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where f.technique_id = :technique_id and f.successful = true 
                group by f.fighter_id, s_date)
                select * from success where fighter_id = :fighter_id order by s_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def singe_leg_takedown_success_rate(cls, params: dict, db: Session):
        technique = db.query(Technique).filter(Technique.name == "Single leg takedown").first()
        params['technique_id'] = technique.id
        statement = text("""
            ---singe_leg_takedown_success_rate_by_year
                with total as (
                        select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as tot_date from fightstatistics f
                        inner join fightinfos f2 on f.fight_id = f2.id
                        
                        where  f.technique_id = :technique_id
                        group by f.fighter_id, tot_date
                        ),
                        success as (
                        select f.fighter_id, count(*) as successful_count, extract(year from f2.fight_date) as suc_date from fightstatistics f
                        inner join fightinfos f2 on f.fight_id = f2.id
                        where  f.technique_id = :technique_id and f.successful = true 
                        group by f.fighter_id, suc_date
                        )
                    select * from (    
                    
                        (select t.fighter_id,coalesce (s.suc_date, t.tot_date) as f_date, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) single_leg_takedown_success_rate
                        from success s right join total t on s.fighter_id = t.fighter_id and s.suc_date = t.tot_date)) where fighter_id = :fighter_id order by f_date	
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch



    @classmethod
    def single_leg_takedown_count(cls, params: dict, db: Session):
        technique = db.query(Technique).filter(Technique.name == "Single leg takedown").first()
        params['technique_id'] = technique.id
        statement = text("""
            ---single_leg_takedown_count_by_year
            with success as (select f.fighter_id,extract(year from f2.fight_date) as s_date, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where f.technique_id = :technique_id and f.successful = true 
                group by f.fighter_id, s_date)
                select * from success where fighter_id = :fighter_id order by s_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch


    @classmethod
    def takedown_count(cls, params: dict, db: Session):
        statement = text("""
            ---takedown_count_by_year
            with success as (select f.fighter_id,extract(year from f2.fight_date) as s_date, count(*) as successful_count from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where f.action_name_id = :action_name_id and f.successful = true 
                group by f.fighter_id, s_date)
            select * from success where fighter_id = :fighter_id order by s_date 
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def average_takedown_points_per_fight(cls, params: dict, db: Session):
        statement = text("""
            ---average_takedown_points_per_fight_by_year
            with avg_takedown_points_per_fight as(
            with fighter_matches as (
            select s.fighter_id, extract(year from i.fight_date) f_date, array_agg(distinct fight_id) fighter_array from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                group by s.fighter_id, extract(year from i.fight_date)
            ),
            opponent_matches as (
            select s.opponent_id, extract(year from i.fight_date) o_date, array_agg(distinct fight_id) opponent_array from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                group by s.opponent_id, extract(year from i.fight_date) 
            ),
            com as (select fighter, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches,
                    f_date
                    from (
            select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array, coalesce(f_date, o_date) f_date
            from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and o_date = f_date
            )),
            takedowns_count as (select f.fighter_id, sum(score) as successful_count, extract(year from f2.fight_date) as f_date  from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            where f.action_name_id = 1 and f.successful = true 
            group by f.fighter_id, extract(year from f2.fight_date)),

            calculation as (
            select fighter, c.f_date, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match
            from com c left join takedowns_count t on c.fighter = t.fighter_id and t.f_date = c.f_date)

            select * from calculation
            )
            select * from avg_takedown_points_per_fight where fighter = :fighter_id  order by f_date	 
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def takedown_per_fight_total(cls, params: dict, db: Session):
        statement = text("""
            ---takedown_per_fight_total_by_year
            with takedown_per_fight_total as (
            with fighter_matches as (
                    select s.fighter_id, array_agg(distinct fight_id) fighter_array, extract(year from i.fight_date) f_date from fightstatistics s
                        inner join fightinfos i on s.fight_id = i.id
                        group by s.fighter_id, extract(year from i.fight_date) 
                    ),
                    opponent_matches as (
                    select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) o_date from fightstatistics s
                        inner join fightinfos i on s.fight_id = i.id
                        group by s.opponent_id, extract(year from i.fight_date) 
                    ),
                    com as (select fighter, cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches,
                            f_date from (
                    select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array , coalesce(f_date, o_date) f_date 
                    from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and o_date = f_date
                    )),
                    takedowns_count as (select f.fighter_id, count(*) as successful_count , extract(year from f2.fight_date) f_date 
                                        from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    inner join actions a on f.action_name_id = a.id
                    where f.action_name_id = 1 and f.successful = true 
                    group by f.fighter_id, extract(year from f2.fight_date)),
                    total as(
                    select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match,
                        c.f_date
                    from com c left join takedowns_count t on c.fighter = t.fighter_id and t.f_date = c.f_date)
                    select * from total 
            )
            select fighter, f_date, tkd_per_match from takedown_per_fight_total where fighter = :fighter_id order by f_date	 
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def takedown_success_rate(cls, params: dict, db: Session):
        statement = text("""
        ---takedown_success_rate_by_year
        with total as (
                select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as tot_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                
                where  f.action_name_id = :action_name_id
                group by f.fighter_id, tot_date
                ),
                success as (
                select f.fighter_id, count(*) as successful_count, extract(year from f2.fight_date) as suc_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                where  f.action_name_id = :action_name_id and f.successful = true 
                group by f.fighter_id, suc_date
                )
            select * from (    
            
                (select t.fighter_id,coalesce (s.suc_date, t.tot_date) as f_date, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
                from success s right join total t on s.fighter_id = t.fighter_id and s.suc_date = t.tot_date)) where fighter_id = :fighter_id order by f_date	 
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch