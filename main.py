import pandas as pd
from typing import Annotated
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.app.models import FightInfo, FightStatistic, Technique, ActionName, Fighter, Tournament
from src.app.base_routres import router as app_routre
from src.app.schemas.fighter_schemas import FighterBase

from src.dashbord.base_routers import router as dashbord_router
from database import engine, Base, session_factory, get_db




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
    dashbord_router,
    prefix="/dashboard",
)
app.include_router(
    app_routre,
    prefix="/app",
)





@app.post("/add-actions-and-techniques")
def add_actions_and_techniques(file: Annotated[bytes, File()]):
    df = pd.read_excel(file)
    df_actions = df['Actions'].drop_duplicates().reset_index(drop=True)
    df_techniques = df['Techniques'].drop_duplicates().reset_index(drop=True)
    
    actions = []
    techniques = []
    with session_factory() as session:
        
        for ac in range(len(df_actions)):
            action = ActionName(name = df_actions[ac])
            actions.append(action)
        session.bulk_save_objects(actions)
        session.commit()
        for te in range(len(df_techniques)):
            print(te)
            technique = Technique(name = df_techniques[te])
            techniques.append(technique)
        session.bulk_save_objects(techniques)
        session.commit()     
    
    
    return {"message": "Success added actions and techniques"}



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
        id_index = session.query(FightInfo).count()
        print(id_index)
        for i in range(id_index,len(df)):

            
            tournament = (
                session.query(Tournament)
                .filter(and_(Tournament.name == df['tournament_name'][i], Tournament.date == df['tournament_date'][i]))
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
            
        if fightinfos!=[]:
            session.bulk_save_objects(fightinfos)
            session.commit()
            

        return {"message": "Success added fight infos"}
    

