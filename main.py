import pandas as pd, numpy as np
from typing import Annotated, List
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


import uuid

def generate_unique_uuid():
    return str(uuid.uuid4())

def time_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(":"))
    return minutes * 60 + seconds

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

@app.post("/add-actions-data/")
def add_actions_data(file: Annotated[bytes, File()]):
    df = pd.read_excel(file)
    df['Flag'].fillna(value=0, inplace=True)
    l = []
    a = df['DB ID'].unique()
    print(len(a))
    for i in a:
        l.append(i)
    fight_statistic_list = []

    with session_factory() as session:
        change = 0
        figh = int(df['DB ID'][0])
        f_id = session.query(FightInfo).filter(FightInfo.id == figh).first()
        f_id.status = df['Status'][0]
        f_id.author = df['Author'][0]
        session.commit()
        try:
            for i in range(len(df)):
                db_id = int(df['DB ID'][i])
                if db_id != figh:
                    figh = db_id
                    f_id = session.query(FightInfo).filter(FightInfo.id == figh).first()
                    f_id.status = df['Status'][i]
                    f_id.author = df['Author'][i]
                    session.commit()

                fighter = session.query(Fighter).filter(Fighter.name == df['Wrestler'][i]).first()
                opponent = session.query(Fighter).filter(Fighter.name == df['Opponent'][i]).first()
                action = session.query(ActionName).filter(ActionName.name == df['Action'][i]).first()
                technique = session.query(Technique).filter(Technique.name == df['Technique'][i]).first()
                print(df['Wrestler'][i], df['Opponent'][i], df['Action'][i], df['Technique'][i])
                print(fighter, opponent, action, technique)
                # print(df['Second'][i])
                fight_statistic = FightStatistic(action_number = generate_unique_uuid(), score = int(df['Score'][i]),
                                    successful = bool(df['Successful'][i]), 
                                    flag = bool(df['Flag'][i]),
                                    defense_reason = bool(df['Defense'][i]), 
                                    fight_id=int(df['DB ID'][i]), 
                                    fighter_id = fighter.id,
                                    opponent_id = opponent.id, 
                                    action_name_id = action.id, 
                                    technique_id = technique.id,
                                    action_time_second = time_to_seconds(df['Second'][i]),
                                    video_link = "swagger"
                                    )
                fight_statistic_list.append(fight_statistic)
                if i % 100 == 0:
                    print(i)
                    session.bulk_save_objects(fight_statistic_list)
                    session.commit()
                    fight_statistic_list = []
        except Exception as e:

            return str(e) + "setr="+ str(i) + "db_id=" +str(int(df['DB ID'][i]))
    return "das"


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
    

