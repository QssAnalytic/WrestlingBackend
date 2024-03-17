from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import or_
from sqlalchemy.sql import text
from sqlalchemy.orm import Session

from src.dashbord.services.left_dashbord_services import medal_left_dashbord_service
from src.dashbord.schemas.section_left_schemas import MetricsOutPut, ChartParams, MetricsChartOutPut, ChartBase, StatsChartOutPut
from src.dashbord.enums import ChartNameEnum, MetricsEnum
from database import get_db
router = APIRouter()


@router.get("/metrics/", response_model=MetricsOutPut)
def metrics(fight_date: str, fighter_id: int, metrics_name: MetricsEnum, db: Session = Depends(get_db)):
    fight_date = tuple(list(map(int, fight_date.split(","))))
    params = {"fight_date": fight_date,  "fighter_id": fighter_id}
    response_obj = {}
    if metrics_name == MetricsEnum.Takedown:
        response_obj = medal_left_dashbord_service.takedown_statistic(params=params, db=db)

    elif metrics_name == MetricsEnum.Defence: 
        response_obj = medal_left_dashbord_service.defence_score_statistic(params=params, db=db)

    elif metrics_name == MetricsEnum.Offence: 
        response_obj = medal_left_dashbord_service.offense_score_statistic(params=params, db=db)

    elif metrics_name == MetricsEnum.Durability:
        response_obj = medal_left_dashbord_service.durability_score_statistic(params=params, db=db)

    return response_obj



@router.get("/stats/")
def metrics(fight_date: str, fighter_id: int, db: Session = Depends(get_db)):
    fight_date = tuple(list(map(int, fight_date.split(","))))
    params = {"fight_date": fight_date,  "fighter_id": fighter_id}
    response = medal_left_dashbord_service.stats_score_statistic(params=params, db=db)
    return response

@router.get("/chart/")
def chart(request_body: ChartParams = Depends(), db: Session = Depends(get_db)):
    params = request_body.dict()
    if params.get('metrics') != None and params.get('chart_name') == ChartNameEnum.MetricsChart:
        r, stats_list = medal_left_dashbord_service.chart_metrics_statistic(params=params, db=db)
        p_model = [ChartBase(year = data[1], score=data[-1]*100).dict() for data in r]
        response = MetricsChartOutPut(data=p_model, stats_list=stats_list).dict()
        return response
    if params.get('stats') != None and params.get('chart_name') == ChartNameEnum.StatsChart:
        res_data = medal_left_dashbord_service.chart_stats_statistic(params=params, db=db)
        p_model = [ChartBase(year = data[1], score=data[-1]).dict() for data in res_data]
        response = StatsChartOutPut(data=p_model, 
                                    start_interval=0,
                                    end_interval=max(p_model, key=lambda x: x["score"])["score"]).dict()
        return response
    raise HTTPException(status_code=400, detail="Invalid parameters")