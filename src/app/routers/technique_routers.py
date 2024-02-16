# from typing import List
# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from database import get_db
# from src.app.crud.crud_techniques import technique
# from src.app.schemas.technique_schemas import TechniqueBaseInfos
# router = APIRouter()

# @router.get("/", response_model=List[TechniqueBaseInfos])
# def get_all_tecneques(db: Session = Depends(get_db)):
#     response = technique.fech_multi(db=db)
#     return response