from datetime import date, datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class CreateFightStatistic(BaseModel):
    action_time: str
    action_time_second: int
    action_number: str
    score: int
    successful: bool
    video_link: HttpUrl
    defense_reason: bool
    fight_id: int
    action_name_id: int
    technique_id: int
    fighter_id: int
    video_second_begin: datetime
    video_second_end: datetime

class GetFightStatistic(CreateFightStatistic):
    id: int

    class Config:
        from_attributes = True