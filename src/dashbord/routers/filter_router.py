from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.dashbord.schemas.countries_schemas import FilterOutPut

from src.app.models import Fighter
from database import get_db
router = APIRouter()

@router.get("/countries/", response_model=FilterOutPut)
def get_all_countries(db: Session = Depends(get_db)):
    pass