from datetime import date
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Union
from decimal import Decimal
from src.dashbord.enums import ChartNameEnum, MetricsEnum, OffenceStatsChartEnum, DefenceStatsChartEnum, TakedownStatsChartEnum,DurabilityStatsChartEnum

class ChartBase(BaseModel):
    year: int
    score: float



class MetricsChartOutPut(BaseModel):
    data: List[ChartBase]
    stats_list: list

class StatsChartOutPut(BaseModel):
    data: List[ChartBase]
    start_interval: int
    end_interval: float


class ChartParams(BaseModel):
    metrics: Optional[MetricsEnum] = Field(None)
    stats: Optional[TakedownStatsChartEnum | OffenceStatsChartEnum | DefenceStatsChartEnum | DurabilityStatsChartEnum] = Field(None)
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