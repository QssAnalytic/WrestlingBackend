from sqlalchemy import text
from database import session_factory
from src.dashbord.enums import DefenceStatsChartEnum
class MetricsChartRepo:

    @classmethod
    def defence_metrics_chart(cls, params: dict):
        defence_stats = [member.value for member in DefenceStatsChartEnum]
        
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
        return fetch, defence_stats
