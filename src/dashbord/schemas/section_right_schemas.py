from datetime import date
from pydantic import BaseModel, validator, root_validator, model_validator, Field
from typing import Optional, List, Union


class GoldBronzeMedalsPlaceOutPut(BaseModel):
    location: str
    stage: str
    fight_date: date
    # @root_validator(pre=True)
    # def transform_data(cls, values):
        
    #     if values['stage'] == "Gold":
    #         values['GoldMedal'] = values['stage']
    #         return values
    #     elif values['stage'] == "Bronze":
    #         values['BronzeMedal'] = values['stage']
    #         return values
    #     return values
        


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



# class MedalsOutPut(BaseModel):
#     Gold: int
#     Bronze: int
#     Silver: int
#     place: List[GoldBronzeMedalsPlaceOutPut]



class FightCountsOutPut(BaseModel):
    win: int
    lose: int
    all_fights: int
    win_rate: int

class WinDecisionResult(BaseModel):
    decision: str
    decision_count: int


class DecisionOutPut(BaseModel):
    win_decision: Union[WinDecisionResult, dict] = Field(union_mode='left_to_right')
    lose_decision: Union[WinDecisionResult, dict] = Field(union_mode='left_to_right')

    class Config:
        from_attributes = True

