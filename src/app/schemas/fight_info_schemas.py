from datetime import date
from pydantic import BaseModel
from typing import Optional, List
from src.app.schemas.fight_statistic_schemas import GetFightStatisticBase
from src.app.schemas.fighter_schemas import FighterBase

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
    fighter: Optional[FighterBase]
    oponent: Optional[FighterBase]
    winner: Optional[FighterBase]

    class Config:
        from_attributes = True

class FightInfoBase(CreateFighterInfo):
    id: int
    fighter: Optional[FighterBase]
    oponent: Optional[FighterBase]
    winner: Optional[FighterBase]
    fight_statistic: Optional[List[GetFightStatisticBase]]
    class Config:
        from_attributes = True


