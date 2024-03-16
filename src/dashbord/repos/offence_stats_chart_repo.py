from sqlalchemy import text
from sqlalchemy.orm import Session
from database import session_factory
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum
from src.app.models import ActionName, Technique


class OffenceStatsChartRepo:

    @classmethod
    def parterre_points_per_fight(cls, params:dict, db:Session):
        technique_names = ['Leg lace', 'Roll from parter', 'Arm-lock roll on parter', 'Gator roll', 'Pin to parter']
        result = db.query(Technique.id).filter(Technique.name.in_(technique_names)).all()
        technique_ids = tuple((row[0] for row in result))
        params['technique_id'] = technique_ids
        statement = text("""
            --Parterre points per fight by year
				with fighter_matches as (
				select s.fighter_id, extract(year from i.fight_date) as year, array_agg(distinct fight_id) fighter_array from fightstatistics s
					inner join fightinfos i on s.fight_id = i.id
					group by s.fighter_id, extract(year from i.fight_date)
				),
				opponent_matches as (
				select s.opponent_id, extract(year from i.fight_date) as year, array_agg(distinct fight_id) opponent_array from fightstatistics s
					inner join fightinfos i on s.fight_id = i.id
					group by s.opponent_id, extract(year from i.fight_date)
				),
				com as (select fighter, year,  cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
				select coalesce(fighter_id, opponent_id) fighter, coalesce(fi.year, op.year) as year, (fighter_array || opponent_array) as combine_array 
				from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = op.opponent_id and fi.year = op.year
				)),
				total_points as (select f.fighter_id, extract(year from f2.fight_date) as year, sum(score) as total_points from fightstatistics f
				inner join fightinfos f2 on f.fight_id = f2.id
				where f.successful = true and f.technique_id in :technique_id
				group by f.fighter_id, extract(year from f2.fight_date))
				select * from (
				select fighter, c.year, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
				from com c left join total_points t on c.fighter = t.fighter_id and c.year = t.year order by year)
	 where fighter = :fighter_id
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch


    @classmethod
    def parterre_count_per_fight(cls, params:dict, db:Session):
        technique_names = ['Leg lace', 'Roll from parter', 'Arm-lock roll on parter', 'Gator roll', 'Pin to parter']
        result = db.query(Technique.id).filter(Technique.name.in_(technique_names)).all()
        technique_ids = tuple((row[0] for row in result))
        params['technique_id'] = technique_ids
        statement = text("""
            --Partere counts per fight by year
            with fighter_matches as (
            select s.fighter_id, array_agg(distinct fight_id) fighter_array, extract(year from i.fight_date) as year from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                group by s.fighter_id, extract(year from i.fight_date)
            ),
            opponent_matches as (
            select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) as year from fightstatistics s
                inner join fightinfos i on s.fight_id = i.id
                group by s.opponent_id,  extract(year from i.fight_date)
            ),
            com as (select fighter, year , cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
            select coalesce(fighter_id, opponent_id) fighter, coalesce(fi.year, op.year)as year, (fighter_array || opponent_array) as combine_array 
            from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.year = op.year
            )),
            successful_roll_attempts as (select f.fighter_id, count(*) as successful_attempts, extract(year from f2.fight_date) as year from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            where f.successful = true and f.technique_id in :technique_id
            group by f.fighter_id, extract(year from f2.fight_date)),
            total_roll_attempts as (select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as year from fightstatistics f
            inner join fightinfos f2 on f.fight_id = f2.id
            inner join actions a on f.action_name_id = a.id
            where f.technique_id in :technique_id
            group by f.fighter_id, extract(year from f2.fight_date))
            select * from (
            select fighter, t.year, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_roll_attempts_per_match
            from successful_roll_attempts t left join total_roll_attempts tc on t.fighter_id = tc.fighter_id and t.year = tc.year
            left join com c on c.fighter = t.fighter_id and c.year = t.year order by t.year)
            where fighter = :fighter_id
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch

    @classmethod
    def parterre_success_rate(cls, params:dict, db:Session):
        technique_names = ['Leg lace', 'Roll from parter', 'Arm-lock roll on parter', 'Gator roll', 'Pin to parter']
        result = db.query(Technique.id).filter(Technique.name.in_(technique_names)).all()
        technique_ids = tuple((row[0] for row in result))
        params['technique_id'] = technique_ids
        statement = text("""
        --parterre success rate by years
			with total as (
						select f.fighter_id, extract(year from f2.fight_date) as year, count(*) as total_count from fightstatistics f
						inner join fightinfos f2 on f.fight_id = f2.id

							where f.technique_id in :technique_id
							group by f.fighter_id, extract(year from f2.fight_date)
							),
							success as (
							select f.fighter_id,extract(year from f2.fight_date) as year,
								count(*) as successful_offense from fightstatistics f
							inner join fightinfos f2 on f.fight_id = f2.id

							where f.successful = true and f.technique_id in :technique_id
							group by f.fighter_id, extract(year from f2.fight_date)
							)
				select * from (
				  select t.fighter_id , coalesce(t.year,s.year) as f_date, round(coalesce(cast(successful_offense as decimal) / cast(total_count as decimal), 0), 2) partere_success_rate
				  from total t 
				  left join success s 
				  on t.fighter_id = s.fighter_id and t.year = s.year) where fighter_id = :fighter_id order by f_date 
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch  


    @classmethod
    def roll_points_per_fight(cls, params:dict, db:Session):
        statement = text("""
            --Roll points per fight by year
				with fighter_matches as (
				select s.fighter_id, extract(year from i.fight_date) as year, array_agg(distinct fight_id) fighter_array from fightstatistics s
					inner join fightinfos i on s.fight_id = i.id
					group by s.fighter_id, extract(year from i.fight_date)
				),
				opponent_matches as (
				select s.opponent_id, extract(year from i.fight_date) as year, array_agg(distinct fight_id) opponent_array from fightstatistics s
					inner join fightinfos i on s.fight_id = i.id
					group by s.opponent_id, extract(year from i.fight_date)
				),
				com as (select fighter, year,  cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
				select coalesce(fighter_id, opponent_id) fighter, coalesce(fi.year, op.year) as year, (fighter_array || opponent_array) as combine_array 
				from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = op.opponent_id and fi.year = op.year
				)),
				total_points as (select f.fighter_id, extract(year from f2.fight_date) as year, sum(score) as total_points from fightstatistics f
				inner join fightinfos f2 on f.fight_id = f2.id
				where f.successful = true and f.action_name_id = 2
				group by f.fighter_id, extract(year from f2.fight_date))
				select * from (
				select fighter, coalesce(c.year,t.year) as f_date, coalesce(round(cast(total_points as decimal)/cast(unique_matches as decimal), 2), 0) as avg_points_per_match
				from com c left join total_points t on c.fighter = t.fighter_id and c.year = t.year order by f_date)
	        where fighter = :fighter_id
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch  

    @classmethod
    def roll_count_per_fight(cls, params:dict, db:Session):
        statement = text("""
        --Roll counts per fight by year
        with fighter_matches as (
        select s.fighter_id, array_agg(distinct fight_id) fighter_array, extract(year from i.fight_date) as year from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            group by s.fighter_id, extract(year from i.fight_date)
        ),
        opponent_matches as (
        select s.opponent_id, array_agg(distinct fight_id) opponent_array, extract(year from i.fight_date) as year from fightstatistics s
            inner join fightinfos i on s.fight_id = i.id
            group by s.opponent_id,  extract(year from i.fight_date)
        ),
        com as (select fighter, year , cardinality(array(select distinct unnest_array from unnest(combine_array) as unnest_array)) unique_matches from (
        select coalesce(fighter_id, opponent_id) fighter, coalesce(fi.year, op.year)as year, (fighter_array || opponent_array) as combine_array 
        from fighter_matches fi full outer join opponent_matches op on fi.fighter_id = opponent_id and fi.year = op.year
        )),
        successful_roll_attempts as (select f.fighter_id, count(*) as successful_attempts, extract(year from f2.fight_date) as year from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where f.successful = true and  f.action_name_id = 2
        group by f.fighter_id, extract(year from f2.fight_date)),
        total_roll_attempts as (select f.fighter_id, count(*) as total_count, extract(year from f2.fight_date) as year from fightstatistics f
        inner join fightinfos f2 on f.fight_id = f2.id
        inner join actions a on f.action_name_id = a.id
        where  f.action_name_id = 2
        group by f.fighter_id, extract(year from f2.fight_date))
        select * from (
        select fighter, coalesce(t.year,tc.year) as f_date, coalesce(round(cast(successful_attempts as decimal)/cast(unique_matches as decimal), 2), 0) as successful_roll_attempts_per_match
        from successful_roll_attempts t left join total_roll_attempts tc on t.fighter_id = tc.fighter_id and t.year = tc.year
        left join com c on c.fighter = t.fighter_id and c.year = t.year order by f_date)
        where fighter = :fighter_id 
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch    

    @classmethod
    def roll_success_rate(cls, params:dict, db: Session):
        statement = text("""
            --roll success rate by years
			with total as (
						select f.fighter_id, extract(year from f2.fight_date) as t_year, count(*) as total_count from fightstatistics f
						inner join fightinfos f2 on f.fight_id = f2.id

							where f.action_name_id = 2
							group by f.fighter_id, extract(year from f2.fight_date)
							),
							success as (
							select f.fighter_id,extract(year from f2.fight_date) as s_year,
								count(*) as successful_offense from fightstatistics f
							inner join fightinfos f2 on f.fight_id = f2.id

							where f.successful = true and f.action_name_id = 2
							group by f.fighter_id, extract(year from f2.fight_date)
							)
				  select t.fighter_id , coalesce(t.t_year,s.s_year) as f_date, round(coalesce(cast(successful_offense as decimal) / cast(total_count as decimal), 0), 2) roll_success_rate
				  from total t 
				  left join success s 
				  on t.fighter_id = s.fighter_id and t.t_year = s.s_year where s.fighter_id = :fighter_id order by f_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch


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