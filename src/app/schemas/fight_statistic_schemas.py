from datetime import date, datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from src.app.schemas.action_schemas import ActionBaseInfos
from src.app.schemas.technique_schemas import TechniqueBaseInfos
from src.app.schemas.fighter_schemas import FighterBase

class CreateFightStatistic(BaseModel):
    # action_time: str
    action_time_second: int
    action_number: str
    score_id: int
    successful: bool
    # author: Optional[str]
    video_link: HttpUrl
    defense_reason: bool
    fight_id: int
    action_name_id: int
    technique_id: int
    fighter_id: int
    opponent_id: Optional[int]
    # video_second_begin: datetime
    # video_second_end: datetime


class StatisticOutPut(BaseModel):

    # action_time: str
    action_time_second: int
    action_number: str
    score: int
    successful: bool
    author: Optional[str]
    video_link: HttpUrl
    defense_reason: bool
    fight_id: int
    action_name_id: int
    technique_id: int
    fighter_id: int
    opponent_id: Optional[int]

class FightStatisticOutPutBase(StatisticOutPut):
    id: int
    fighter: Optional[FighterBase]
    opponent: Optional[FighterBase]
    action_name: Optional[ActionBaseInfos]
    technique: Optional[TechniqueBaseInfos]
    class Config:
        from_attributes = True

class UpdateFightStatistic(CreateFightStatistic):
    __annotations__ = {k: Optional[v] for k, v in CreateFightStatistic.__annotations__.items()}

class FightStatistic(BaseModel):
    action_time: Optional[str]
    action_time_second: int
    action_number: str
    score: int
    successful: bool
    video_link: HttpUrl
    defense_reason: bool
    fight_id: int
    action_name: ActionBaseInfos
    technique: TechniqueBaseInfos
    fighter: FighterBase
    video_second_begin: Optional[datetime]
    video_second_end: Optional[datetime]

class GetFightStatisticBase(FightStatistic):
    id: int

    class Config:
        from_attributes = True