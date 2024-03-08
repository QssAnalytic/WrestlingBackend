from datetime import date
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Union
from decimal import Decimal

class MetricsList(BaseModel):
    metrics: str
    score: float
    successful_count: int
    total_count: int | float
    bar_pct: float

class MetricsOutPut(BaseModel):
    name: str
    metrics_list: List[MetricsList]