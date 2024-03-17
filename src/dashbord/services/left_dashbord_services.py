from datetime import datetime
from typing import Generic, TypeVar, Type

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.app.models import FightInfo, Technique, ActionName
from src.dashbord.enums import ChartNameEnum, MetricsEnum, TakedownStatsChartEnum
from src.dashbord.utils.takedown_utils import *
from src.dashbord.utils.defence_score_utils import *
from src.dashbord.utils.offence_score_utils import *
from src.dashbord.utils.stats_takedown_utils import *
from src.dashbord.utils.durability_score_utils import *
from src.dashbord.services.chart_services import *

from database import Base, engine, get_db, session_factory

ModelTypeVar = TypeVar('ModelTypeVar', bound=Base)







class MedalLeftDashbordSerivices(Generic[ModelTypeVar]):
    def __init__(self, model: Type[ModelTypeVar], metrics_services: ChartMetricsServices, stats_services: ChartStatsServices) -> None:
        self.model = model
        self.metrics_services = metrics_services
        self.stats_services = stats_services


    def chart_metrics_statistic(self, params: dict, db:Session):
        if params.get('metrics') == MetricsEnum.Defence:
            r, stats_list = self.metrics_services.defence_metrics_chart(params=params)
            return r, stats_list
        elif params.get('metrics') == MetricsEnum.Takedown:
            r, stats_list = self.metrics_services.takedown_metrics_chart(params=params)
            return r, stats_list
        
        elif params.get('metrics') == MetricsEnum.Offense:
            r, stats_list = self.metrics_services.offence_metrics_chart(params=params)
            return r, stats_list
        
        elif params.get('metrics') == MetricsEnum.Durability:
            r, stats_list = self.metrics_services.durability_metrics_chart(params=params, db=db)
            return r, stats_list
        return None

    def chart_stats_statistic(self, params: dict, db: Session):
        r = self.stats_services.get_stats_statistic(params=params, db=db)
        return r

            

    def stats_score_statistic(self, params: dict, db: Session):
        obj = {'metrics': '',
            'score': 0,
            'successful_count':0,
            'total_count':0,
            'bar_pct': 0}
        response_list = []
        stats_takedown_obj = stats_takedown(session_factory=session_factory, params=params, obj=obj, db=db)
        stats_defence_obj = stats_defence(session_factory=session_factory, params=params, obj=obj, db=db)
        stats_offence_obj = stats_offence(session_factory=session_factory, params=params, obj=obj, db=db)
        stats_durability_obj =stats_durability(session_factory=session_factory, params=params, obj=obj, db=db)
        response_list.append(stats_takedown_obj)
        response_list.append(stats_offence_obj)
        response_list.append(stats_defence_obj)
        response_list.append(stats_durability_obj)
        return response_list
    

    def durability_score_statistic(self, params: dict, db: Session):
        obj = {'metrics': '',
            'score': 0,
            'successful_count':0,
            'total_count':0,
            'bar_pct': 0,
            'star': False}
        response = {}
        response = {}
        response['name'] = 'Durability Score'
        takedown_durability_score_obj = takedown_durability_score_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        defence_durability_score_obj = defence_durability_score_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        offence_durability_score_obj = offence_durability_score_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        passivity_durability_per_fight_obj = passivity_durability_per_fight(session_factory=session_factory, params=params, obj=obj, db=db)
        total_late_defences_per_fight_obj = total_late_defences_per_fight_utils(session_factory=session_factory, params=params, obj=obj, model=self.model,db=db)
        total_late_attempts_per_fight_obj = total_late_attempts_per_fight_utils(session_factory=session_factory, params=params, obj=obj, model=self.model,db=db)
        response_list = []
        response_list.append(total_late_attempts_per_fight_obj)
        response_list.append(total_late_defences_per_fight_obj)
        response_list.append(passivity_durability_per_fight_obj)
        response_list.append(takedown_durability_score_obj)
        response_list.append(defence_durability_score_obj)
        response_list.append(offence_durability_score_obj)



        response['metrics_list'] = response_list
        return response
    

    def offense_score_statistic(self, params:dict, db: Session):
        obj = {'metrics': '',
            'score': 0,
            'successful_count':0,
            'total_count':0,
            'bar_pct': 0,
            'star': False}
        response_list = []
        response = {}
        response['name'] = 'Offense Score'
        action_success_rate_obj = offence_action_success_rate_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        action_count_per_fight_obj = offence_action_count_per_fight(session_factory=session_factory, params=params, obj=obj, db=db)
        offence_action_point_per_fight_obj = offence_action_point_per_fight(session_factory=session_factory, params=params, obj=obj, db=db)
        # offence_protection_zone_success_rate_obj = offence_protection_zone_success_rate(session_factory=session_factory, params=params, obj=obj, db=db)
        offence_protection_count_per_fight_obj = offence_protection_count_per_fight(session_factory=session_factory, params=params, obj=obj, db=db)
        # protection_zone_points_per_fight_obj = protection_zone_points_per_fight_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        roll_success_rate_obj = roll_success_rate_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        roll_points_per_fight_obj = roll_points_per_fight_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        roll_count_per_fight_obj = roll_count_per_fight_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        parterre_success_rate_obj = parterre_success_rate_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        parterre_count_rate_obj = parterre_count_rate_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        parterre_points_rate_obj = parterre_points_rate_utils(session_factory=session_factory, params=params, obj=obj, db=db)
        response_list.append(action_success_rate_obj)
        response_list.append(action_count_per_fight_obj)
        response_list.append(offence_action_point_per_fight_obj)
        # response_list.append(offence_protection_zone_success_rate_obj)
        response_list.append(offence_protection_count_per_fight_obj)

        # response_list.append(protection_zone_points_per_fight_obj)
        response_list.append(roll_success_rate_obj)
        response_list.append(roll_count_per_fight_obj)
        response_list.append(roll_points_per_fight_obj)
        response_list.append(parterre_success_rate_obj)
        response_list.append(parterre_count_rate_obj)
        response_list.append(parterre_points_rate_obj)
        response['metrics_list'] = response_list
        return response

    def defence_score_statistic(self, params:dict, db: Session):
        obj = {'metrics': '',
            'score': 0,
            'successful_count':0,
            'total_count':0,
            'bar_pct': 0,
            'star': False}
        response_list = []
        response = {}
        response['name'] = 'Defence Score'
    

        action_escape_rate_obj = action_escape_rate_utils(session_factory=session_factory, params=params, obj = obj, db=db)
        pin_to_parter_escape_rate_obj = pin_to_parter_escape_rate_utils(session_factory=session_factory, params=params,obj=obj, db=db)
        takedown_escape_rate_obj = takedown_escape_rate_utils(session_factory=session_factory, params=params,obj = obj, db=db)
        roll_escape_rate_obj= roll_escape_rate_utils(session_factory=session_factory, params=params,obj=obj, db=db)
        # protection_zone_escape_rate_obj = protection_zone_escape_rate_utils(session_factory=session_factory, params=params,obj=obj, db=db)
        parterre_escape_rate_obj = parterre_escape_rate_utils(session_factory=session_factory, params=params, obj=obj, model=self.model,db=db)
        action_skipped_points_per_fight_obj = action_skipped_points_per_fight_utils(session_factory=session_factory, params=params, obj=obj, model=self.model,db=db)
        
        response_list.append(action_escape_rate_obj)
        response_list.append(action_skipped_points_per_fight_obj)
        response_list.append(takedown_escape_rate_obj)
        response_list.append(pin_to_parter_escape_rate_obj)
        response_list.append(roll_escape_rate_obj)
        # response_list.append(protection_zone_escape_rate_obj)
        response_list.append(parterre_escape_rate_obj)


        
        response['metrics_list'] = response_list
        return response

    def takedown_statistic(self, params: dict, db: Session):
        action = db.query(ActionName).filter(ActionName.name == 'Takedown').first()
        params['action_name_id'] = action.id
        obj = {'metrics': '',
            'score': 0,
            'successful_count':0,
            'total_count':0,
            'bar_pct': 0,
            'star': False}
        response = {}
        response['name'] = 'Takedown Score'
        response_list = []
        takedown_success_rate_obj = takedown_success_rate_utils(params=params, obj = obj, session_factory=session_factory)
        takedown_per_match_obj = takedown_per_match_utils(session_factory=session_factory, params=params, obj = obj)
        takedown_average_points_per_fight_obj = takedown_average_points_per_fight_utils(session_factory=session_factory, params=params, obj = obj)
        takedown_count_obj = takedown_count_utils(session_factory=session_factory, params=params, obj = obj)
        double_leg_takedown_count_obj = double_leg_takedown_count_utils(session_factory=session_factory, params=params,model=self.model,obj = obj, db=db)
        single_leg_takedown_success_obj = single_leg_takedown_success_rate_utils(session_factory=session_factory, params=params, model=self.model, obj=obj, db=db)
        single_leg_takedown_count_obj = single_leg_takedown_count_utils(session_factory=session_factory, params=params, model=self.model,obj=obj, db=db)
        double_leg_takedown_success_rate_obj = double_leg_takedown_success_rate_utils(session_factory=session_factory, params=params, model=self.model,obj=obj, db=db)

        response_list.append(takedown_success_rate_obj)
        response_list.append(takedown_per_match_obj)
        response_list.append(takedown_average_points_per_fight_obj)
        response_list.append(takedown_count_obj)

        response_list.append(single_leg_takedown_count_obj)
        response_list.append(single_leg_takedown_success_obj)
        
        response_list.append(double_leg_takedown_count_obj)
        response_list.append(double_leg_takedown_success_rate_obj)
        response['metrics_list'] = response_list
        return response
    

    
medal_left_dashbord_service = MedalLeftDashbordSerivices(Technique, 
                                                         metrics_services=ChartMetricsServices, 
                                                         stats_services=ChartStatsServices)
