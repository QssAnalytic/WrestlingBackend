from datetime import date
from fastapi import Query
from pydantic import BaseModel, Field, ValidationError, validator
from typing import Optional, List
from src.app.schemas.fight_statistic_schemas import FightStatisticOutPutBase
from src.app.schemas.fighter_schemas import FighterBase
from src.app.schemas.tournament_schemas import TournamentBaseInfos
from src.app.enums import SourceTypeEnum, StatusEnum, OrderEnum
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
    opponent1: str | int
    opponent2: str | int
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



class UpdateFighterInfo(BaseModel):
    level: str
    oponent1_point: int
    oponent2_point: int
    fight_date: date
    location: str
    wrestling_type: str
    weight_category: int
    stage: str
    decision: str
    author: str
    status: StatusEnum
    source_type: SourceTypeEnum
    submited_date: date
    checked_date: date
    created_date: date
    fighter_id: int
    oponent_id: int
    winner_id: int
    tournament_id: int


class UpdateFightInfoAuthorStatusOrder(BaseModel):
    order: Optional[OrderEnum]
    author: Optional[str]
    status: Optional[StatusEnum]
    check_author: Optional[str]

    @validator("author")
    def check_author(cls, author):
        if author == None or author == '':
            return None
        return author
        
    
    @validator("check_author")
    def check_author_check(cls, check_author):
        if check_author == None or check_author == '':
            return None
        return check_author
        
    class Config:
        from_attributes = True


class AllFightInfoBase(CreateFighterInfo):
    id: int
    author: Optional[str]
    check_author: Optional[str]
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
    order: Optional[OrderEnum]
    author: Optional[str]
    status: Optional[StatusEnum]
    check_author: Optional[str]
    fighter: Optional[FighterBase]
    oponent: Optional[FighterBase]
    winner: Optional[FighterBase]
    tournament: TournamentBaseInfos
    fight_statistic: Optional[List[FightStatisticOutPutBase]]
    class Config:
        from_attributes = True


class FilterFightInfoBase(BaseModel):
    tournament_id: Optional[int] = Field(None)
    place: Optional[str] = Field(None)
    wrestler_name: Optional[str] = Field(None)
    author: Optional[str] = Field(None)
    is_submitted: Optional[bool] = Field(None)
    status: Optional[str] = Field(None)
    weight_category: Optional[str] = Field(None)
    date: Optional[int] = Field(None)
    stage: Optional[str] = Field(None)
    wrestling_type: Optional[str] = Field(None)
    check_author: Optional[str] = Field(Query(None))
    page: Optional[int] = Field(Query(1, ge=0))
    limit:int=Field(Query(100, ge=100))



# tournament_id: int | None = None, place: str | None = None, wrestler_name: str | None = None,
#                 author: str | None = None, is_submitted: bool | None = None, status: str | None = None,
#                 weight_category: int | None = None, date: int | None = None, stage: str | None = None,
#                 wrestling_type: str | None = None, check_author: str | None = None,
#                 page: int = Query(1, ge=0),limit:int=Query(100, ge=100)