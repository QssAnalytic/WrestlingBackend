from src.app.crud.base import CRUDBase
from src.app.models import FightStatistic
from src.app.schemas.fight_statistic_schemas import CreateFightStatistic

class CRUDStatistic(CRUDBase[FightStatistic,CreateFightStatistic]):
    ...

statistic = CRUDStatistic(FightStatistic)