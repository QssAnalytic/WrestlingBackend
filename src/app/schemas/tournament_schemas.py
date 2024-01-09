from datetime import date
from pydantic import BaseModel
from typing import Optional, List

class TournamentCreate(BaseModel):
    name: str

class TournamentBaseInfos(TournamentCreate):
    id: int