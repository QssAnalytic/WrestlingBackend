from datetime import date
from pydantic import BaseModel
from typing import Optional, List
from src.app.schemas.fight_statistic_schemas import GetFightStatistic
from src.app.schemas.fighter_schemas import FighterResponse

class CreateFighterInfo(BaseModel):
    wrestling_type: str
    fight_date: date
    location: str
    weight_category: str
    stage: str
    author: str
    decision: str
    oponent1_point: int
    oponent2_point: int


class AllFightInfoBase(CreateFighterInfo):
    id: int
    fighter: Optional[FighterResponse]
    oponent: Optional[FighterResponse]
    winner: Optional[FighterResponse]

    class Config:
        from_attributes = True

class FightInfoBase(CreateFighterInfo):
    id: int
    fighter: Optional[FighterResponse]
    oponent: Optional[FighterResponse]
    winner: Optional[FighterResponse]
    fight_statistic: Optional[List[GetFightStatistic]]
    class Config:
        from_attributes = True