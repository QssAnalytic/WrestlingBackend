from typing import TypeVar
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base
from src.app.models import ActionName


def offence_protection_count_per_fight(engine, params: dict, obj:dict, db: Session):
    obj_copy = obj.copy()