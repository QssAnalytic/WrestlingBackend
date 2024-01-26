from datetime import date
from pydantic import BaseModel, Field
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
    is_submitted: bool
    status: str
    oponent1_point: int
    oponent2_point: int
    level: str


class CreateFighterInfoBase(BaseModel):
    opponent1_name: str
    opponent2_name: str
    opponent1_nationality: str
    opponent2_nationality: str
    level: str
    location: str
    wrestling_type: str
    weight_category: int
    stage: str
    decision: str
    tournament_date: date
    tournament_name: str



class UpdateFighterInfo(CreateFighterInfo):
    pass


class AllFightInfoBase(CreateFighterInfo):
    id: int
    author: Optional[str]
    submited_date: Optional[date]
    checked_date: Optional[date]
    created_date: Optional[date]
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
    author: Optional[str]
    fighter: Optional[FighterBase]
    oponent: Optional[FighterBase]
    winner: Optional[FighterBase]
    tournament: TournamentBaseInfos
    fight_statistic: Optional[List[FightStatisticOutPutBase]]
    class Config:
        from_attributes = True


