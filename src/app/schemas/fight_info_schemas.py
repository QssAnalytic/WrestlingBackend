from datetime import date
from pydantic import BaseModel
from typing import Optional, List
from src.app.schemas.fight_statistic_schemas import FightStatisticOutPutBase
from src.app.schemas.fighter_schemas import FighterBase
from src.app.schemas.tournament_schemas import TournamentBaseInfos

class CreateFighterInfo(BaseModel):
    wrestling_type: str
    fight_date: date
    location: str
    weight_category: int
    stage: str
    decision: str
    oponent1_point: int
    oponent2_point: int
    level: str

class UpdateFighterInfo(BaseModel):
    pass





class AllFightInfoBase(CreateFighterInfo):
    id: int
    fighter: Optional[FighterBase]
    oponent: Optional[FighterBase]
    winner: Optional[FighterBase]
    tournament: TournamentBaseInfos

    class Config:
        from_attributes = True


class FightInfoOut(BaseModel):
    count: int
    next_page: Optional[int]
    previous_page: Optional[int]
    data: List[AllFightInfoBase]


class FightInfoBase(CreateFighterInfo):
    id: int
    fighter: Optional[FighterBase]
    oponent: Optional[FighterBase]
    winner: Optional[FighterBase]
    tournament: TournamentBaseInfos
    fight_statistic: Optional[List[FightStatisticOutPutBase]]
    class Config:
        from_attributes = True


