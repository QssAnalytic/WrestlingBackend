from datetime import date
from pydantic import BaseModel
from typing import Optional, List



class Fighter(BaseModel):
    name: str
    # level: str
    # birth_date: date
    natinality_name: str

class FighterBase(Fighter):
    id: int

    class Config:
        from_attributes = True






