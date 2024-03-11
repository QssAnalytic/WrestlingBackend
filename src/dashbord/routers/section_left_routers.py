from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import or_
from sqlalchemy.sql import text
from sqlalchemy.orm import Session

from src.dashbord.services.left_dashbord_services import medal_left_dashbord_service
from src.dashbord.schemas.section_left_schemas import MetricsOutPut, ChartParams, MetricsChartOutPut, MetricsChartBase
from src.dashbord.enums import MetricsEnum
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

    elif metrics_name == MetricsEnum.Offense: 
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

@router.get("/chart/", response_model=MetricsChartOutPut)
def chart(request_body: ChartParams = Depends()):
    params = request_body.dict()
    response_list = []
    r, stats_list = medal_left_dashbord_service.chart_statistic(params=params)
    p_model = [MetricsChartBase(year = data[1], score=data[-1]*100) for data in r]
    response = MetricsChartOutPut(data=p_model, stats_list=stats_list)
    return response