from pydantic import BaseModel
from typing import Optional

class ActionBase(BaseModel):
    name: str

class ActionoutPut(ActionBase):
    id: int