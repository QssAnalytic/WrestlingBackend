import pandas as pd
from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from database import engine, Base, session_factory
from src.app.models import *

app = FastAPI()


@app.post("/add-nationalty")
def add_nationalty(file: Annotated[bytes, File()]):
    df = pd.read_excel(file)
    op1_national = df['Opponent1 nation']
    op2_national = df['Opponent2 nation']
    final_nation = pd.concat([op1_national, op2_national]).drop_duplicates()
    
    with session_factory() as session:
        for index in final_nation:
            nationality = Nationality(name = index)
            session.add(nationality)
        session.commit()
    return {"message": "Success added nationalty"}



@app.post("/add-fighter")
def add_fighter(file: Annotated[bytes, File()]):
    pass
