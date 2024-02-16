from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import column, literal_column
from sqlalchemy import func, cast, DECIMAL, Float, select

from src.app.models import *
from src.dashbord.services import medal_dashbord_service
from src.dashbord.schemas.section_right_schemas import MedalsOutPut, FightCountsOutPut, DecisionOutPut, TestOutPut
from database import get_db

router = APIRouter()


@router.get("/medal-filter/", response_model=MedalsOutPut)
def filter_by_medal(fighter_id: int, year: str, db: Session = Depends(get_db)):
    response = medal_dashbord_service.get_medals_count(fighter_id=fighter_id, year=year, db=db)
    gold_bronze_response, silver_response, bronze_response = medal_dashbord_service.get_medals_list(fighter_id=fighter_id, year=year, db=db)
    response_obj = response
    response_obj['gold_place'] = gold_bronze_response
    response_obj['silver_place'] = silver_response
    response_obj['bronze_place'] = bronze_response
    return response_obj

@router.get("/get-fight-count/", response_model=FightCountsOutPut)
def get_all_fight_count(fighter_id: int, year:str, db: Session = Depends(get_db)):
    response  = medal_dashbord_service.get_fights_count(fighter_id=fighter_id, year=year, db=db)
    return response

@router.get("/get-total-point/")
def get_total_fighter_point(fighter_id: int, year:str, db: Session = Depends(get_db)):
    response  = medal_dashbord_service.get_total_points(fighter_id=fighter_id, year=year, db=db)
    return response


@router.get("/get-decisions/", response_model=DecisionOutPut)
def get_decision_average(fighter_id: int, year:str, db: Session = Depends(get_db)):
    response = medal_dashbord_service.get_decision_point(fighter_id=fighter_id, year=year, db=db)
    return response



@router.get("/test")
def test(session = Depends(get_db)):
    fightstats = aliased(FightStatistic)
    fightinfos = aliased(FightInfo)
    techniques = aliased(Technique)

    subquery_a = (
        session.query(
            fightstats.fighter_id,
            func.extract('year', fightinfos.fight_date).label('fight_year'),
            fightstats.technique_id,
            func.count().label('successful_count')
        )
        .join(fightinfos, fightstats.fight_id == fightinfos.id)
        .join(techniques, fightstats.technique_id == techniques.id)
        .filter(fightstats.action_name_id == 1, fightstats.successful == True)
        .group_by(fightstats.fighter_id, func.extract('year', fightinfos.fight_date), fightstats.technique_id)
        .subquery()
    )

    
    subquery_b = (
        session.query(
            fightstats.fighter_id,
            func.extract('year', fightinfos.fight_date).label('fight_year'),
            fightstats.technique_id,
            func.count().label('total_count')
        )
        .join(fightinfos, fightstats.fight_id == fightinfos.id)
        .join(techniques, fightstats.technique_id == techniques.id)
        .filter(fightstats.action_name_id == 1)
        .group_by(fightstats.fighter_id, func.extract('year', fightinfos.fight_date), fightstats.technique_id)
        .subquery()
    )
    
    ranked_data = (
        session.query(
            subquery_a.c.fighter_id,
            subquery_a.c.fight_year,
            subquery_a.c.technique_id,
            subquery_a.c.successful_count,
            subquery_b.c.total_count,
            (cast(subquery_a.c.successful_count, Float) / cast(subquery_b.c.total_count, Float)).label('statistic')
        )
        .join(subquery_b, subquery_a.c.fighter_id == subquery_b.c.fighter_id)
        .filter(subquery_a.c.fight_year == subquery_b.c.fight_year, subquery_a.c.technique_id == subquery_b.c.technique_id)
        .subquery()
    )
    
    # rank_column = func.row_number().over(partition_by=[ranked_data.c.fight_year, ranked_data.c.technique_id]).label('rank')
    # rank_values = session.query(ranked_data.c.fight_year, ranked_data.c.technique_id, func.max(rank_column).over()).all()
    # print(rank_values)

    rank_column = func.row_number().over(
    partition_by=[ranked_data.c.fight_year, ranked_data.c.technique_id]
    ).label('rank')

    # Subquery to calculate the ranks
    subquery = (
        session.query(
            ranked_data,
            rank_column
        )
        .subquery()
    )

    # Query to calculate the maximum rank within each partition
    max_rank_column = func.max(subquery.c.rank).over(
        partition_by=[subquery.c.fight_year, subquery.c.technique_id]
    ).label('max_rank')

    # Final query to retrieve the results
    rank_values = session.query(
        subquery.c.fight_year,
        subquery.c.technique_id,
        max_rank_column
    ).all()
    print(rank_values)
#     final_query = (
#     session.query(
#         ranked_data,
#         (func.ROUND(1 - cast(rank_column, Float) / cast(func.max(rank_column).over(), Float), 2)).label('final_rank')
#     )
# ).all()
    return "l"
