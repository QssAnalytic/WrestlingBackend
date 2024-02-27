from pydantic import BaseModel
from typing import Optional

class ActionBase(BaseModel):
    data: str

class ActionoutPut(ActionBase):
    id: int