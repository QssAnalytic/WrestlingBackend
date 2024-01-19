from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete, update, extract,func, Integer
from sqlalchemy.orm import Session

from database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, id:int, db:Session) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
        
    
    def get_multi(self, date:int, db:Session) -> Optional[ModelType]:
        data = db.execute(select(self.model).filter(func.extract('year',self.model.date).cast(Integer) == date)).scalars().all()
        return data

    def create(self, data: CreateSchemaType, db: Session)-> ModelType:
        data_obj = jsonable_encoder(data)
        db_data = self.model(**data_obj)
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        return db_data
    
    def update(self, id:int, data: UpdateSchemaType, db: Session):
        db_data = self.get(id=id, db=db)
        data_obj = jsonable_encoder(data)
        db.execute(
            update(self.model)
            .filter(self.model.id==id)
            .values(**data_obj)
        )
        db.commit()
        db.refresh(db_data)
        return db_data


    def delete(self, id: int, db: Session):
        db.execute(
            delete(self.model).filter(self.model.id==id)
        )
        db.commit()