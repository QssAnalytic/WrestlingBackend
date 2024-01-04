from datetime import date
from pydantic import BaseModel
from typing import Optional, List

class TechniqueNameCreate(BaseModel):
    name: str

class TechniqueBaseInfos(TechniqueNameCreate):
    id: int