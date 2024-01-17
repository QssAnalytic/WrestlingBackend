from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select
from src.app.models import FightInfo
class FightInfoPagination:
    def __init__(self, session: Session, page:int, limit:int, query):
        self.page = page
        self.limit = limit
        self.offset = (page-1)*limit
        self.db=session
        self.query = query

    def _get_next_page(self):
        pass

    def _get_previous_page(self):
        pass

    def _total_page_count(self):
        total_records = self.query.count()
        return (total_records + self.limit - 1) // self.limit

    def get_response(self):
        data = self.query.options(
            joinedload(FightInfo.fighter,  innerjoin=True),
            joinedload(FightInfo.oponent,  innerjoin=True),
            joinedload(FightInfo.winner,  innerjoin=True),
            joinedload(FightInfo.tournament,  innerjoin=True)
        ).order_by(FightInfo.id).offset(self.offset).limit(self.limit)
        return {
            'count':self._total_page_count(),
            'data':data
        }
