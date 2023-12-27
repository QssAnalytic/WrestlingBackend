from pydantic import BaseModel
from typing import Optional

class ActionNameCreate(BaseModel):
    name: str

class ActionBaseInfos(ActionNameCreate):
    id: int