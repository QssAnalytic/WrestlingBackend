from sqlalchemy import text
from sqlalchemy.orm import Session
from database import session_factory
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum
from src.app.models import ActionName, Technique


class DefenceStatsChartRepo:

    @classmethod
    def parterre_escape_rate(cls, params:dict, db:Session):
        technique_names = ['Leg lace', 'Roll from parter', 'Arm-lock roll on parter', 'Gator roll', 'Pin to parter']
        result = db.query(Technique.id).filter(Technique.name.in_(technique_names)).all()
        technique_ids = tuple((row[0] for row in result))
        params['technique_id'] = technique_ids
        statement = text("""                        
            --parterre_escape_rate
            with total as (
	            select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
	            inner join fightinfos f2 on f.fight_id = f2.id
                where f.technique_id in :technique_id
	            group by f.opponent_id, t_date
	           	),
				success as (
					select f.opponent_id, count(*) as successful_escape, extract(year from f2.fight_date) s_date from fightstatistics f
					inner join fightinfos f2 on f.fight_id = f2.id
					where  f.successful = false and f.technique_id in :technique_id
					group by f.opponent_id, s_date
                    ),
               calculation as (
                    select t.opponent_id,coalesce(t.t_date,s.s_date) as f_date,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
                        from total t left join success s on s.opponent_id = t.opponent_id and t.t_date = s.s_date)  
                    select * from calculation where opponent_id = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def protection_zone_escape_rate(cls, params:dict, db:Session):
        action = db.query(ActionName).filter(ActionName.name == "Protection zone").first()
        params['action_name_id'] = action.id
        statement = text("""                        
            --protection_zone_escape_rate
            with total as (
	            select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
	            inner join fightinfos f2 on f.fight_id = f2.id
                where f.action_name_id = :action_name_id
	            group by f.opponent_id, t_date
	           	),
				success as (
					select f.opponent_id, count(*) as successful_escape, extract(year from f2.fight_date) s_date from fightstatistics f
					inner join fightinfos f2 on f.fight_id = f2.id
					where  f.successful = false and f.action_name_id = :action_name_id
					group by f.opponent_id, s_date
                    ),
               calculation as (
                    select t.opponent_id,coalesce(t.t_date,s.s_date) as f_date,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
                        from total t left join success s on s.opponent_id = t.opponent_id and t.t_date = s.s_date)  
                    select * from calculation where opponent_id = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch


    @classmethod
    def roll_escape_rate(cls, params: dict, db:Session):
        action = db.query(ActionName).filter(ActionName.name == 'Roll').first()
        params['action_name_id'] = action.id
        statement = text("""                        
            --roll_escape_rate
            with total as (
	            select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
	            inner join fightinfos f2 on f.fight_id = f2.id
                where f.action_name_id = :action_name_id
	            group by f.opponent_id, t_date
	           	),
				success as (
					select f.opponent_id, count(*) as successful_escape, extract(year from f2.fight_date) s_date from fightstatistics f
					inner join fightinfos f2 on f.fight_id = f2.id
					where  f.successful = false and f.action_name_id = :action_name_id
					group by f.opponent_id, s_date
                    ),
               calculation as (
                    select t.opponent_id,coalesce(t.t_date,s.s_date) as f_date,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
                        from total t left join success s on s.opponent_id = t.opponent_id and t.t_date = s.s_date)  
                    select * from calculation where opponent_id = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def pin_to_parter_escape_rate(cls, params: dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == "Pin to parter").first()
        params['action_name_id'] = action.id
        statement = text("""
            --pin to parterre escape rate
                with total as (
                            select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
                            inner join fightinfos f2 on f.fight_id = f2.id
                                
                                where f.action_name_id = :action_name_id
                                group by f.opponent_id, t_date
                                ),
                                success as (
                                select f.opponent_id, count(*) as successful_escape, extract(year from f2.fight_date) as s_date from fightstatistics f
                                inner join fightinfos f2 on f.fight_id = f2.id
                
                                where f.successful = false and f.action_name_id = :action_name_id
                                group by f.opponent_id, s_date
                                ),
                    
                calculation as (
                select t.opponent_id,coalesce(t.t_date,s.s_date) as f_date,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 1), 2) action_escape_rate
                    from total t left join success s on s.opponent_id = t.opponent_id and s.s_date = t.t_date)  
                select * from calculation where opponent_id = :fighter_id order by f_date
            """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def takedown_escape_rate(cls, params: dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == 'Takedown').first()
        params['action_name_id'] = action.id
        statement = text("""                        
            --takedown escape rate
            with total as (
	            select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
	            inner join fightinfos f2 on f.fight_id = f2.id
                where f.action_name_id = :action_name_id
	            group by f.opponent_id, t_date
	           	),
				success as (
					select f.opponent_id, count(*) as successful_escape, extract(year from f2.fight_date) s_date from fightstatistics f
					inner join fightinfos f2 on f.fight_id = f2.id
					where  f.successful = false and f.action_name_id = :action_name_id
					group by f.opponent_id, s_date
                    ),
               calculation as (
                    select t.opponent_id,coalesce(t.t_date,s.s_date) as f_date,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
                        from total t left join success s on s.opponent_id = t.opponent_id and t.t_date = s.s_date)  
                    select * from calculation where opponent_id = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch


    @classmethod
    def action_skipped_points_per_fight(cls, params: dict, db: Session):
        statement = text("""                        
        --Action skipped points per fight
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
                com as (select fighter,com_date,cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
                select coalesce(fighter_id, opponent_id) fighter, (fighter_array || opponent_array) as combine_array,coalesce(fi.fi_date, op.op_date) as com_date
                from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.fi_date = op.op_date
                )),
                total_points as (select f.opponent_id, sum(score) as total_points, extract(year from f2.fight_date) as total_date from fightstatistics f
                inner join fightinfos f2 on f.fight_id = f2.id
                inner join actions a on f.action_name_id = a.id
                where f.successful = true
                group by f.opponent_id, total_date),
                calculation as(
                select fighter,coalesce(t.total_date,c.com_date) as cal_date, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
                from com c left join total_points t on c.fighter = t.opponent_id and t.total_date = c.com_date)
            select * from (
            select *, round(cast(avg_points_per_match as decimal)/ cast(max(avg_points_per_match) over() as decimal), 2) from calculation
        ) where fighter = :fighter_id order by cal_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def action_escape_rate(cls, params: dict, db: Session):
        statement = text("""                        
        --action escape rate
            with total as (
	            select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as t_date from fightstatistics f
	            inner join fightinfos f2 on f.fight_id = f2.id
	            group by f.opponent_id, t_date
	           	),
				success as (
					select f.opponent_id, count(*) as successful_escape, extract(year from f2.fight_date) s_date from fightstatistics f
					inner join fightinfos f2 on f.fight_id = f2.id
					where  f.successful = false 
					group by f.opponent_id, s_date
                    ),
               calculation as (
                    select t.opponent_id,coalesce(t.t_date,s.s_date) as f_date,round(coalesce(cast(successful_escape as decimal) / cast(total_count as decimal), 0), 2) action_escape_rate
                        from total t left join success s on s.opponent_id = t.opponent_id and t.t_date = s.s_date)  
                    select * from calculation where opponent_id = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch