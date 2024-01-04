from src.app.crud.base import CRUDBase
from src.app.models import Technique
from src.app.schemas.fight_statistic_schemas import CreateFightStatistic


class CRUDTechnique(CRUDBase[Technique,CreateFightStatistic]):
    ...

technique = CRUDTechnique(Technique)