from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi.encoders import jsonable_encoder
from src.app.crud.base import CRUDBase
from src.app.models import FightInfo, FightStatistic, Tournament, Fighter
from src.app.schemas.fight_info_schemas import CreateFighterInfo, UpdateFighterInfo, CreateFighterInfoBase
from src.app.helpers import FightInfoPagination

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
    
    def create_fightinfo(self, data: CreateFighterInfoBase, db: Session):
        data_dict = jsonable_encoder(data)
        tournament = Tournament(name = data_dict['tournament_name'], date=data_dict['tournament_date'])
        db.add(tournament)
        db.commit()
        db.refresh(tournament)
        fighter = db.query(Fighter).filter(Fighter.name==data_dict['fight_name']).first()
        opponent = db.query(Fighter).filter(Fighter.name==data_dict['opponent_name']).first()
        # winner = db.query(Fighter).filter(Fighter.name==data_dict['winner_name']).first()
        fight_info = FightInfo(
            wrestling_type = data_dict['wrestling_type'],
            fight_date = data_dict['fight_date'],
            location = data_dict['location'],
            weight_category = data_dict['weight_category'],
            stage = data_dict['stage'],
            source_type = 'app',
            decision = data_dict['decision'],
            oponent1_point = data_dict['oponent1_point'],
            oponent2_point = data_dict['oponent2_point'],
            level = data_dict['level'],
            is_submitted = data_dict['is_submitted'],
            status = data_dict['status'],
            
            fighter_id = fighter.id,
            oponent_id = opponent.id,
            winner_id = fighter.id,
            tournament_id = tournament.id
        )
        # db.add(fight_info)
        # db.commit()
        # db.refresh(fight_info)
        return fight_info


fight_info = CRUDFightInfos(FightInfo)