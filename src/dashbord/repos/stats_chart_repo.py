from sqlalchemy import text
from sqlalchemy.orm import Session
from database import session_factory
from src.dashbord.repos.takedown_stats_chart_repo import TakeDownStatsChartRepo
from src.dashbord.repos.defence_chart_repo import DefenceStatsChartRepo
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum
from src.app.models import ActionName, Technique
class StatsChartRepo(TakeDownStatsChartRepo, DefenceStatsChartRepo):
    ...


    