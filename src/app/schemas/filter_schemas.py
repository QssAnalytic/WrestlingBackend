from datetime import date
from pydantic import BaseModel
from typing import Optional, List

class WeightOutPutBase(BaseModel):
    weight_category: int

class StageOutPutBase(BaseModel):
    stage: str