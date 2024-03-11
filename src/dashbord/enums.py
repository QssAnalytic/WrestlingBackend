from enum import Enum

class MetricsEnum(Enum):
    Takedown = "Takedown Score"
    Defence = "Defence Score"
    Offense = "Offense Score"
    Durability = "Durability Score"


class ChartNameEnum(Enum):
    MetricsChart = "MetricsChart"
    StatsChart = "StatsChart"