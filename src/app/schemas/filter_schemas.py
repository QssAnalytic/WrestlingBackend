from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional, List

class WeightOutPutBase(BaseModel):
    weight_category: int


class WrestlingStyleOutPutBase(BaseModel):
    wrestling_type: str

class DateOutPutBase(BaseModel):
    date: int

class StageOutPutBase(BaseModel):
    stage: str