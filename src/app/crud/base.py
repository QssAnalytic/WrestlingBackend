from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, id:int, db:Session) -> Optional[ModelType]:
        data = select(self.model).filter(self.model.id==id).first()
        return data

    def create(self, data: CreateSchemaType, db: Session)-> ModelType:
        data_obj = jsonable_encoder(data)
        db_data = self.model(**data_obj)
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return db_data