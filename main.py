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
    df = pd.read_excel(file)
    op1 = df[['Opponent1','Opponent1 nation']].drop_duplicates()

    op2 = df[['Opponent2','Opponent2 nation']].drop_duplicates()
    print(op2.columns)
    op2.rename(columns = {'Opponent2': 'Opponent1', 'Opponent2 nation' : 'Opponent1 nation'}, inplace=True)
    
    final_op = pd.concat([op1, op2],ignore_index=True)

    with session_factory() as session:
        for i in range(len(final_op)):
            op_name = final_op['Opponent1'][i]
            nationality = (
            session.query(Nationality)
            .filter(Nationality.name ==  final_op['Opponent1 nation'][i])
            .first()
            )
        
            fighter = Fighter(name=op_name, 
                              birth_date = date(1990, 5, 15),
                              nationality_id = nationality.id,
                              level = "Seniors")
            session.add(fighter)
        session.commit()

    return {"message": "Success added fighters"}


@app.post("/add-tournament")
def add_fighter(file: Annotated[bytes, File()]):
    df = pd.read_excel(file)
    tournaments = df['Tournament Name'].drop_duplicates()
    with session_factory() as session:
        for tour in tournaments:
            tournament = Tournament(name = tour)
            session.add(tournament)
        session.commit()


    return {"message": "Success added tournaments"}

@app.post("/add-fight-info")
def add_fight_info(file: Annotated[bytes, File()]):
    df = pd.read_excel(file)
    with session_factory() as session:
        for i in range(len(df)):
            tornament = (
                session.query(Tournament)
                .filter(Tournament.name == df['Tournament Name'][i])
                .first()
            )