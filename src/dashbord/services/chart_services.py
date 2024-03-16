from sqlalchemy.orm import Session
from src.app.models import ActionName
from src.dashbord.repos.metrics_chart_repo import MetricsChartRepo
from src.dashbord.repos.stats_chart_repo import StatsChartRepo
from src.dashbord.enums import DefenceStatsChartEnum, TakedownStatsChartEnum, OffenceStatsChartEnum, DefenceStatsChartEnum, DurabilityStatsChartEnum


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

    @classmethod
    def durability_metrics_chart(cls, params: dict):
        data, offence_stats = super().durability_metrics_chart(params=params)
        return data, offence_stats
    

class ChartStatsServices(StatsChartRepo):

    @classmethod
    def get_stats_statistic(cls, params: dict, db: Session):
        response_data = None
        if params.get('stats') == TakedownStatsChartEnum.Takedown_Success_rate:
            response_data = super().takedown_success_rate(params=params, db=db)
        elif params.get('stats') == TakedownStatsChartEnum.Takedown_per_fight_total:
            response_data = super().takedown_per_fight_total(params=params, db=db)
        elif params.get('stats') == TakedownStatsChartEnum.Average_takedown_points_per_fight:
            response_data = super().average_takedown_points_per_fight(params=params, db=db)
        elif params.get('stats') == TakedownStatsChartEnum.Takedown_Count:
            response_data = super().takedown_count(params=params, db=db)
        elif params.get('stats') == TakedownStatsChartEnum.Single_leg_takedown_count:
            response_data = super().single_leg_takedown_count(params=params, db=db)
        elif params.get('stats') == TakedownStatsChartEnum.Singe_Leg_takedown_Success_Rate:
            response_data = super().singe_leg_takedown_success_rate(params=params, db=db)
        elif params.get('stats') == TakedownStatsChartEnum.Double_leg_takedown_counts:
            response_data = super().double_leg_takedown_count(params=params, db=db)
        elif params.get('stats') == TakedownStatsChartEnum.Double_leg_takedown:
            response_data = super().double_leg_takedown_success_rate(params=params, db=db)
        #------------------------------- DEFFENCE ------------------------------------------
        elif params.get('stats') == DefenceStatsChartEnum.Action_escape_rate:
            response_data = super().action_escape_rate(params=params, db=db)
        elif params.get('stats') == DefenceStatsChartEnum.Action_skipped_points_per_fight:
            response_data = super().action_skipped_points_per_fight(params=params, db=db)
        elif params.get('stats') == DefenceStatsChartEnum.Takedown_escape_rate:
            response_data = super().takedown_escape_rate(params=params, db=db)
        elif params.get('stats') == DefenceStatsChartEnum.Pin_to_parter_escape_rate:
            response_data = super().pin_to_parter_escape_rate(params=params, db=db)
        elif params.get('stats') == DefenceStatsChartEnum.Roll_escape_rate:
            response_data = super().roll_escape_rate(params=params, db=db)
        elif params.get('stats') == DefenceStatsChartEnum.Protection_zone_escape_rate:
            response_data = super().protection_zone_escape_rate(params=params, db=db)
        elif params.get('stats') == DefenceStatsChartEnum.Parterre_escape_rate:
            response_data = super().parterre_escape_rate(params=params, db=db)
        #------------------------------- OFFENCE ------------------------------------------
        elif params.get('stats') == OffenceStatsChartEnum.Action_Success_rate:
            response_data = super().action_escape_rate(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Action_count_per_fight:
            response_data = super().action_counts_per_fight(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Action_points_per_fight:
            response_data = super().action_point_per_fight(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Protection_zone_success_rate:
            response_data = super().protection_zone_success_rate(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Protection_zone_count_per_fight:
            response_data = super().protection_zone_counts_per_fight(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Protection_zone_points_per_fight:
            response_data = super().protection_zone_points_per_fight(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Roll_success_rate:
            response_data = super().roll_success_rate(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Roll_count_per_fight:
            response_data = super().roll_count_per_fight(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Roll_points_per_fight:
            response_data = super().roll_points_per_fight(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Parterre_success_rate:
            response_data = super().parterre_success_rate(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Parterre_count_per_fight:
            response_data = super().parterre_count_per_fight(params=params, db=db)
        elif params.get('stats') == OffenceStatsChartEnum.Parterre_points_per_fight:
            response_data = super().parterre_points_per_fight(params=params, db=db)
        #------------------------------- DURABILITY ------------------------------------------
        elif params.get('stats') == DurabilityStatsChartEnum.Total_successful_defenses_per_fight_2nd_part:
            response_data = super().total_successful_defenses_per_fight_2nd_part(params=params, db=db)
        elif params.get('stats') == DurabilityStatsChartEnum.Total_action_counts_per_fight_2nd_part:
            response_data = super().total_action_counts_per_fight_2nd_part(params=params, db=db)
        elif params.get('stats') == DurabilityStatsChartEnum.Passivity_per_fight:
            response_data = super().passivity_per_fight(params=params, db=db)
        return response_data