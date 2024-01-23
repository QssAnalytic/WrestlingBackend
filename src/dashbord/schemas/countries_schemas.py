from pydantic import BaseModel
from typing import Optional


class FilterOutPut(BaseModel):
    data: int | str