from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Integer, func, select, text, or_
from src.dashbord.schemas.countries_schemas import FilterOutPut

from src.app.models import Fighter, FightInfo
from database import get_db
router = APIRouter()

@router.get("/countries/", response_model=List[FilterOutPut])
def get_all_countries(db: Session = Depends(get_db)):
    query = text("SELECT DISTINCT natinality_name FROM fighters ORDER BY natinality_name")
    result = db.execute(query).fetchall()
    nationalities = [res[0] for res in result]
    return [FilterOutPut(data=nat) for nat in nationalities]


@router.get("/fighters/{country_name}/", response_model=List[dict])
def get_fighters(country_name: str,db: Session = Depends(get_db)):
    sql_query = text("SELECT id, name FROM fighters WHERE natinality_name = :country_name") 
    
    try:
        response = db.execute(sql_query, {"country_name": country_name}).fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    fighters = [{'id': row.id, 'data': row.name} for row in response]
    return fighters


@router.get("/years/{wrestler_id}/", response_model=List[FilterOutPut])
def get_years(wrestler_id: int, db: Session = Depends(get_db)):
    response = db.execute(
        select(
            func.extract('year', FightInfo.fight_date).cast(Integer)
        )
        .filter(
            or_(
                FightInfo.fighter_id == wrestler_id,
                FightInfo.oponent_id == wrestler_id
            )
        )
        .distinct(
            func.extract('year', FightInfo.fight_date)
        )
    ).scalars().all()
    return [FilterOutPut(data=row) for row in response]
