from datetime import date
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Union


class GoldBronzeMedalsPlaceOutPut(BaseModel):
    location: str
    stage: str
    fight_date: date


class SilverMedalsPlaceOutPut(BaseModel):
    location: str
    stage: str = "Silver"
    fight_date: date
    class Config:
        validate_assignment = True

    @validator('stage', check_fields=False)
    def set_stage(cls, stage):
        return 'Silver'

class MedalsOutPut(BaseModel):
    Gold: int
    Bronze: int
    Silver: int
    gold_place: List[GoldBronzeMedalsPlaceOutPut]
    silver_place: List[SilverMedalsPlaceOutPut]
    bronze_place: List[GoldBronzeMedalsPlaceOutPut]



class FightCountsOutPut(BaseModel):
    win: int
    lose: int
    all_fights: int
    win_rate: int
    score_by_weight: float
    score_by_style: float

class WinDecisionResult(BaseModel):
    decision: str
    decision_count: int


class DecisionOutPut(BaseModel):
    win_decision: List[WinDecisionResult]
    lose_decision: List[WinDecisionResult]

    class Config:
        from_attributes = True


class TestOutPut(BaseModel):
    fighter_id: int
    fight_year: int
    technique_id: int
    successful_count: int
    total_count: int
    statistic: float

