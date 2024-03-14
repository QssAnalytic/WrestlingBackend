from enum import Enum

class MetricsEnum(Enum):
    Takedown = "Takedown Score"
    Defence = "Defence Score"
    Offense = "Offence Score"
    Durability = "Durability Score"


class ChartNameEnum(Enum):
    MetricsChart = "MetricsChart"
    StatsChart = "StatsChart"


class OffenceStatsChartEnum(Enum):
    Action_Success_rate = "Action Success rate"
    Action_count_per_fight = "Action count per fight" 
    Action_points_per_fight = "Action points per fight"
    Protection_zone_success_rate = "Protection zone success rate"
    Protection_zone_count_per_fight = "Protection zone count per fight"
    Protection_zone_points_per_fight = "Protection zone points per fight"
    Roll_success_rate = "Roll success rate"
    Roll_count_per_fight = "Roll count per fight"
    Roll_points_per_fight = "Roll points per fight"
    Parterre_success_rate = "Parterre success rate"
    Parterre_count_per_fight = "Parterre count per fight"
    Parterre_points_per_fight = "Parterre points per fight"


class TakedownStatsChartEnum(Enum):
    Takedown_Success_rate = "Takedown Success rate"
    Takedown_per_fight_total = "Takedown per fight total"
    Average_takedown_points_per_fight = "Average takedown points per fight"
    Takedown_Count = "Takedown Count"
    Single_leg_takedown_count = "Single leg takedown count"
    Singe_Leg_takedown_Success_Rate = "Single Leg takedown Success Rate"
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

