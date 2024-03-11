from enum import Enum

class MetricsEnum(Enum):
    Takedown = "Takedown Score"
    Defence = "Defence Score"
    Offense = "Offense Score"
    Durability = "Durability Score"


class ChartNameEnum(Enum):
    MetricsChart = "MetricsChart"
    StatsChart = "StatsChart"


class TakedownStatsChartEnum(Enum):
    Takedown_Success_rate = "Takedown Success rate"
    Takedown_per_fight_total = "Takedown per fight total"
    Average_takedown_points_per_fight = "Average takedown points per fight"
    Takedown_Count = "Takedown Count"
    Single_leg_takedown_count = "Single leg takedown count"
    Singe_Leg_takedown_Success_Rate = "Singe Leg takedown Success Rate"
    Double_leg_takedown_counts = "Double leg takedown counts"
    Double_leg_takedown = "Double leg takedown"



class DefenceStatsChartEnum(Enum):
    Action_escape_rate = "Action escape rate"
    Action_skipped_points_per_fight = "Action skipped points per fight"
    Takedown_escape_rate = "Takedown escape rate"
    Pin_to_parter_escape_rate = "Pin to parter escape rate"
    Roll_escape_rate = "Roll escape rate"
    Protection_zone_escape_rate = "Protection zone escape rate"
    Parterre_escape_rate = "Parterre escape rate"