from datetime import date
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Union
from decimal import Decimal
from src.dashbord.enums import ChartNameEnum, MetricsEnum


class MetricsChartOutPut(BaseModel):
    year: int
    score: float


class ChartParams(BaseModel):
    metrics: Optional[MetricsEnum] = Field(None)
    stats: Optional[str] = Field(None)
    chart_name: ChartNameEnum = Field()
    fighter_id: int = Field()


class MetricsList(BaseModel):
    metrics: str
    score: float
    successful_count: int
    total_count: int | float
    bar_pct: float

class MetricsOutPut(BaseModel):
    name: str
    metrics_list: List[MetricsList]