from datetime import date
from pydantic import BaseModel
from typing import Optional, List

class TechniqueNameCreate(BaseModel):
    name: str


class UpdateTechnique(BaseModel):
    pass
class TechniqueBaseInfos(TechniqueNameCreate):
    id: int

