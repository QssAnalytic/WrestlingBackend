from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional, List

class WeightOutPutBase(BaseModel):
    data: int

class DateOutPutBase(BaseModel):
    date: int

class StageOutPutBase(BaseModel):
    stage: int