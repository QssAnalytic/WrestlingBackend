from datetime import date
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Union
from decimal import Decimal

class MetricsOutPut(BaseModel):
    metrics: str
    score: Decimal