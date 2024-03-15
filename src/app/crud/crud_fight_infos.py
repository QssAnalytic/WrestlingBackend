from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi.encoders import jsonable_encoder
from src.app.crud.base import CRUDBase
from src.app.models import FightInfo, FightStatistic, Tournament, Fighter
from src.app.schemas.fight_info_schemas import CreateFighterInfo, UpdateFighterInfo, CreateFighterInfoBase, UpdateFightInfoAuthorStatusOrder
from src.app.helpers import FightInfoPagination
from src.app.helpers import get_currenct_date

class CRUDFightInfos(CRUDBase[FightInfo,CreateFighterInfoBase, UpdateFighterInfo]):

    def get_multi(self, db:Session, page:Optional[int], limit: int, data: FightInfo) -> List[FightInfo]:
        # data = db.query(FightInfo)
        count = data.count()
        total_page = (count + limit - 1) // limit
        pagination = FightInfoPagination(session=db, page=page, limit=limit, query = data, count=count, total_page=total_page) 
        return pagination.get_response()

    def get_by_id(self, id:int, db:Session) -> Optional[FightInfo]:
        data = db.execute(
        select(FightInfo).filter(FightInfo.id==id).options(
        joinedload(FightInfo.fighter),
        joinedload(FightInfo.oponent),
        joinedload(FightInfo.winner),
        joinedload(FightInfo.tournament),
        joinedload(FightInfo.fight_statistic).joinedload(FightStatistic.action_name)
        )
        ).scalars().unique().first()
        return data
    
    def create_fight_info(self, data: CreateFighterInfoBase, db: Session):
        data_dict = jsonable_encoder(data)
        opponent1_id_or_name = data_dict['opponent1']
        opponent2_id_or_name = data_dict['opponent2']
        if type(opponent1_id_or_name) == int:
            opponent1 = db.query(Fighter).filter(Fighter.id==opponent1_id_or_name).first()
        else:
            opponent1 = Fighter(name=opponent1_id_or_name, natinality_name=data_dict['opponent1_nationality'])
            db.add(opponent1)

        if type(opponent2_id_or_name) == int:
            opponent2 = db.query(Fighter).filter(Fighter.id==opponent2_id_or_name).first()
        else:
            opponent2 = Fighter(name=opponent2_id_or_name, natinality_name=data_dict['opponent2_nationality'])
            db.add(opponent2)
        
        existing_tournament = db.query(Tournament).filter(Tournament.name == data_dict['tournament_name']).first()

        if existing_tournament is None:
            # Tournament does not exist, so add it
            tournament = Tournament(name=data_dict['tournament_name'], date=data_dict['tournament_date'])
            db.add(tournament)
            db.commit()
            db.refresh(tournament)
        else:
            tournament = existing_tournament

        fight_info_db = FightInfo(
            wrestling_type = data_dict['wrestling_type'],
            fight_date = data_dict['tournament_date'],
            location = data_dict['location'],
            weight_category = data_dict['weight_category'],
            stage = data_dict['stage'],
            source_type = 'app',
            decision = data_dict['decision'],
            oponent1_point = 0,
            oponent2_point = 0,
            level = data_dict['level'],            
            fighter_id = opponent1.id,
            oponent_id = opponent2.id,
            winner_id = opponent1.id,
            tournament_id = tournament.id,
            created_date = get_currenct_date()
        )
        db.add(fight_info_db)
        db.commit()
        db.refresh(fight_info_db)
        return fight_info_db
    
    def update_status(self, id:int, data: UpdateFightInfoAuthorStatusOrder, db: Session):
        fight_info = self.get(id=id, db=db)
        current_date = get_currenct_date()
        
        data_obj = jsonable_encoder(data)
        status = data_obj['status']
        if fight_info == None:
            return HTTPException(status_code=404, detail="content not found")

        if status == "completed":
            if fight_info.submited_date is None:
                fight_info.submited_date = current_date
            fight_info.status = status
            fight_info.is_submitted = False
        elif status == "in progress":
            fight_info.status = status
            fight_info.is_submitted = False
        elif status == "not started":
            fight_info.status = status
            fight_info.is_submitted = False

        elif status == "checked":
            fight_info.checked_date = current_date
            fight_info.is_submitted = True
            fight_info.status = "checked"
            fight_info.check_author = data_obj['check_author']
        fight_info.author = data_obj['author']
        fight_info.order = data_obj['order']
        db.commit()
        db.refresh(fight_info)
        return fight_info
    



fight_info = CRUDFightInfos(FightInfo)