from datetime import date
from pydantic import BaseModel
from typing import Optional, List



class FighterBase(BaseModel):
    name: str
    level: str
    birth_date: date
    natinality_name: str

class FighterResponse(FighterBase):
    id: int

    class Config:
        from_attributes = True






