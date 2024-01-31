from pydantic import BaseModel, validator
from typing import Optional, List


class GoldBronzeMedalsPlaceOutPut(BaseModel):
    location: str
    stage: str

class SilverMedalsPlaceOutPut(BaseModel):
    location: str
    stage: str = "Silver"
    class Config:
        validate_assignment = True

    @validator('stage', check_fields=False)
    def set_stage(cls, stage):
        return 'Silver'

class MedalsOutPut(BaseModel):
    Gold: int
    Bronze: int
    Silver: int
    place: List[GoldBronzeMedalsPlaceOutPut]
    silver_place: List[SilverMedalsPlaceOutPut]