import re
import pandas as pd
from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, session_factory, get_db
from src.app.models import *
from src.app.routers import actions_routers, fight_infos_routers, statistics_routers, technique_routers
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fight_infos_routers.router,
    prefix="/fight-infos",
    tags=["fight-infos"]
)
app.include_router(
    statistics_routers.router,
    prefix="/statistics",
    tags=["statistics"]
)
app.include_router(
    actions_routers.router,
    prefix="/actions",
    tags=["actions"]
)

app.include_router(
    technique_routers.router,
    prefix="/techniques",
    tags=["techniques"]
)


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
    
    op2.rename(columns = {'Opponent2': 'Opponent1', 'Opponent2 nation' : 'Opponent1 nation'}, inplace=True)
    
    final_op = pd.concat([op1, op2],ignore_index=True)
    final_op = final_op.drop_duplicates(subset=['Opponent1']).reset_index(drop=True)
    
    
    with session_factory() as session:
        fighters = []
        for i in range(len(final_op)):
            print(i)
            op_name = final_op['Opponent1'][i]
            print(op_name)
        
            fighter = Fighter(name=op_name, 
                              birth_date = date(1990, 5, 15),
                              natinality_name = final_op['Opponent1 nation'][i],
                              level = "Seniors")
            fighters.append(fighter)
        session.bulk_save_objects(fighters)
        session.commit()

    return {"message": "Success added fighters"}


@app.post("/add-tournament")
def add_fighter(file: Annotated[bytes, File()]):
    df = pd.read_excel(file)
    tournaments_df = df[['tournament_name', 'tournament_date']].drop_duplicates(subset=['tournament_name', 'tournament_date']).reset_index(drop=True)
    

    with session_factory() as session:
        tournaments = []
        for tour in range(len(tournaments_df)):

            tournament = Tournament(name = tournaments_df['tournament_name'][tour], date=tournaments_df['tournament_date'][tour])
            tournaments.append(tournament)
        session.bulk_save_objects(tournaments)
        session.commit()


    return {"message": "Success added tournaments"}

@app.post("/add-fight-info")
def add_fight_info(file: Annotated[bytes, File()]):
    df = pd.read_excel(file)
    with session_factory() as session:
        fightinfos = []
        id_index = session.execute(select(FightInfo).order_by(FightInfo.id.desc())).scalars().first()
        for i in range(id_index.id-502,len(df)):

            
            tournament = (
                session.query(Tournament)
                .filter(Tournament.name == df['tournament_name'][i])
                .first()
            )
            
            fighter = (
                session.query(Fighter)
                .filter(Fighter.name == df['opponent1'][i])
                .first()
            )
            
            opponent = (
                session.query(Fighter)
                .filter(Fighter.name == df['opponent2'][i])
                .first()
            )
            print("i=",i)
            print("opponent1=",df['opponent1'][i])
            print("opponent2=",df['opponent2'][i])
            print("opponent1_point=",int(df['opponent1_points'][i]))
            print("opponent1_point=",int(df['opponent2_points'][i]))
            
            fightinfo = FightInfo(wrestling_type = df['style'][i],
                                  fight_date = df['tournament_date'][i],
                                  location = df['place'][i],
                                  weight_category = int(df['weight'][i].split()[0]),
                                  stage = df['stage'][i],
                                  decision = df['decision'][i],
                                  oponent1_point = int(df['opponent1_points'][i]),
                                  oponent2_point = int(df['opponent2_points'][i]),
                                  tournament_id = tournament.id,
                                  fighter_id = fighter.id,
                                  oponent_id = opponent.id,
                                  winner_id = fighter.id)
            fightinfos.append(fightinfo)
            if i==id_index.id-502+4000:
                break
        if fightinfos!=[]:
            session.bulk_save_objects(fightinfos)
            session.commit()
        return {"message": "Success added fight infos"}