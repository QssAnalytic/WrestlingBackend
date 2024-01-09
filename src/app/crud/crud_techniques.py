from src.app.crud.base import CRUDBase
from src.app.models import Technique
from src.app.schemas.technique_schemas import TechniqueNameCreate, UpdateTechnique


class CRUDTechnique(CRUDBase[Technique,TechniqueNameCreate, UpdateTechnique]):
    ...

technique = CRUDTechnique(Technique)