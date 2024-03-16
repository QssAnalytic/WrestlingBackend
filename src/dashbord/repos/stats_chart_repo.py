from src.dashbord.repos.offence_stats_chart_repo import OffenceStatsChartRepo
from src.dashbord.repos.takedown_stats_chart_repo import TakeDownStatsChartRepo
from src.dashbord.repos.defence_chart_repo import DefenceStatsChartRepo

class StatsChartRepo(TakeDownStatsChartRepo, DefenceStatsChartRepo, OffenceStatsChartRepo):
    ...


    