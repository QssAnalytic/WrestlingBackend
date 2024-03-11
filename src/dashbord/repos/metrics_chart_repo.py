from sqlalchemy import text
from database import session_factory
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum
class MetricsChartRepo:

    @classmethod
    def defence_metrics_chart(cls, params: dict):
        stats_list = [member.value for member in DefenceStatsChartEnum]
        
        statement = text("""
            with action_escape_rate as(
                with total as (
                    select f.opponent_id, count(*) as total_count, extract(year from f2.fight_date) as total_date from fightstatistics f       	
                    inner join fightinfos f2 on f.fight_id = f2.id
                    group by f.opponent_id, extract(year from f2.fight_date)),
                success as (
                    select f.opponent_id, count(*) as successful_escape, extract(year from f2.fight_date) as success_date from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    where f.successful = false 
                    group by f.opponent_id, extract(year from f2.fight_date)
                    ),
                calculation as (
                    select t.opponent_id, t.total_count, 
                    t.total_date, 
                    successful_escape, 
                    s.success_date, 
                    round(cast(coalesce(successful_escape, 0)as decimal) /cast(total_count as decimal), 2) as action_escape_rate
                    from total t 
                    left join success s on s.opponent_id = t.opponent_id and t.total_date = s.success_date
                )
                select * from (select opponent_id, action_escape_rate, total_date,
                        round((action_escape_rate) /(max(action_escape_rate) over()), 2) bar_pct
                        from calculation)
            )
            select * from(
            select *, round(1 - cast(defense_rank as decimal) / cast(max(defense_rank) over() as decimal), 2) from(
            select *, rank() over(order by bar_pct desc) defense_rank from(
            select opponent_id,total_date, bar_pct from action_escape_rate))) where opponent_id = :fighter_id order by total_date 
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch, stats_list
    
    @classmethod
    def takedown_metrics_chart(cls, params: dict):
        stats_list = [member.value for member in TakedownStatsChartEnum]
        
        statement = text("""
            --takedown_score
            with takedown_success as(
            with total as (
                    select f.fighter_id, count(*) as total_count, extract(year from fight_date) t_date from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    where f.action_name_id = 1
                    group by f.fighter_id, extract(year from fight_date)
                    ),
                    success as (
                    select f.fighter_id, count(*) as successful_count, extract(year from fight_date) s_date from fightstatistics f
                    inner join fightinfos f2 on f.fight_id = f2.id
                    where f.action_name_id = 1 and f.successful = true 
                    group by f.fighter_id, extract (year from fight_date)
                    )
                select * from (    
                select fighter_id,t_date, takedown_success_rate, successful_count, total_count,round((takedown_success_rate - min(takedown_success_rate) over()) /(max(takedown_success_rate) over() - min(takedown_success_rate) over()), 2) tkd_bar_pct from 
                    (select t.fighter_id, t_date, coalesce(successful_count, 0) successful_count, total_count, round(coalesce(cast(successful_count as decimal) / cast(total_count as decimal), 0), 2) takedown_success_rate
                    from success s right join total t on s.fighter_id = t.fighter_id and t_date = s_date))),
            avg_takedown_points_per_fight as(
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
            select fighter, coalesce(round(cast(successful_count as decimal)/cast(unique_matches as decimal), 2), 0) as tkd_per_match, c.f_date
            from com c left join takedowns_count t on c.fighter = t.fighter_id and t.f_date = c.f_date)

            select * from (select fighter, tkd_per_match, f_date,
                        round((tkd_per_match - min(tkd_per_match) over( partition by f_date)) /(max(tkd_per_match) over(partition by f_date) - min(tkd_per_match) over(partition by f_date)), 2) count_bar_pct
                        from calculation)),
            takedown_per_fight_total as (
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
                    select * from (
                    select *, round((tkd_per_match - 0) /(max(tkd_per_match) over(partition by f_date) - 0), 2) bar_pct from total t) 
            )
                select * from (
                    select *, round(1 - cast(tkd_rank as decimal) / cast(max(tkd_rank) over() as decimal), 2) from(
                select *, rank() over(order by score_pct desc) tkd_rank from (
                select fighter_id,t_date, (tkd_bar_pct + bar_pct + count_bar_pct)/3 score_pct from takedown_success t
                left join avg_takedown_points_per_fight a
                    on t.fighter_id = a.fighter and t.t_date = a.f_date
                left join takedown_per_fight_total f
                on t.fighter_id = f.fighter and t.t_date = f.f_date
            ))) where fighter_id = :fighter_id order by t_date
        """)
        with session_factory() as session:
            exc = session.execute(statement, params)
            fetch = exc.fetchall()
        return fetch, stats_list
    
