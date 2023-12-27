from datetime import date
from pydantic import BaseModel
from typing import Optional

class FighterBase(BaseModel):
    name: str
    level: str
    birth_date: date
    natinality_name: str

class FighterResponse(FighterBase):
    id: int

    class Config:
        from_attributes = True

class FightInfoBase(BaseModel):

    wrestling_type: str
    fight_date: date
    location: str
    weight_category: str
    stage: str
    author: str
    decision: str
    oponent1_point: int
    oponent2_point: int
    fighter: Optional[FighterResponse]
    oponent: Optional[FighterResponse]
    winner: Optional[FighterResponse]
    class Config:
        from_attributes = True

