from sqlalchemy.orm import Session
from src.app.models import ActionName
from src.dashbord.repos.metrics_chart_repo import MetricsChartRepo
from src.dashbord.repos.stats_chart_repo import StatsChartRepo
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum


class ChartMetricsServices(MetricsChartRepo):

    @classmethod
    def defence_metrics_chart(cls, params: dict):
        data, defence_stats = super().defence_metrics_chart(params=params)
        return data, defence_stats
    
    @classmethod
    def takedown_metrics_chart(cls, params: dict):
        data, takedown_stats = super().takedown_metrics_chart(params=params)
        return data, takedown_stats
    
    @classmethod
    def offence_metrics_chart(cls, params: dict):
        data, offence_stats = super().offence_metrics_chart(params=params)
        return data, offence_stats
    

class ChartStatsServices(StatsChartRepo):

    @classmethod
    def get_stats_statistic(cls, params: dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == 'Takedown').first()
        params['action_name_id'] = action.id
        if params.get('stats') == TakedownStatsChartEnum.Takedown_Success_rate:
            response_data = super().takedown_success_rate(params=params, db=db)

        if params.get('stats') == TakedownStatsChartEnum.Takedown_per_fight_total:
            response_data = super().takedown_per_fight_total(params=params, db=db)

        if params.get('stats') == TakedownStatsChartEnum.Average_takedown_points_per_fight:
            response_data = super().average_takedown_points_per_fight(params=params, db=db)
        if params.get('stats') == TakedownStatsChartEnum.Takedown_Count:
            response_data = super().takedown_count(params=params, db=db)
        if params.get('stats') == TakedownStatsChartEnum.Single_leg_takedown_count:
            response_data = super().single_leg_takedown_count(params=params, db=db)
        if params.get('stats') == TakedownStatsChartEnum.Singe_Leg_takedown_Success_Rate:
            response_data = super().singe_leg_takedown_success_rate(params=params, db=db)
        if params.get('stats') == TakedownStatsChartEnum.Double_leg_takedown_counts:
            response_data = super().double_leg_takedown_count(params=params, db=db)
        if params.get('stats') == TakedownStatsChartEnum.Double_leg_takedown:
            response_data = super().doible_leg_takedown_success_rate(params=params, db=db)
        return response_data