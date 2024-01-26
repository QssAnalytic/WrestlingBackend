import datetime
import pytz
from typing import TypeVar
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select
from src.app.models import FightInfo

from database import Base

ModelType = TypeVar("ModelType", bound=Base)

class FightInfoPagination:
    def __init__(self, session: Session, page:int, limit:int, query, count:int, total_page: int):
        self.page = page
        self.limit = limit
        self.offset = (page-1)*limit
        self.db=session
        self.query = query
        self.count = count
        self.total_page = total_page

    def _get_next_page(self):
        
        if self.page < self.total_page and self.total_page!=1:
            return self.page+1
        return None

    def _get_previous_page(self):
        if self.page == 1:
            return None
        return self.page - 1

    def _total_page_count(self):
        
        return self.total_page

    def get_response(self):
        data = self.query.options(
            joinedload(FightInfo.fighter,  innerjoin=True),
            joinedload(FightInfo.oponent,  innerjoin=True),
            joinedload(FightInfo.winner,  innerjoin=True),
            joinedload(FightInfo.tournament,  innerjoin=True)
        ).order_by(FightInfo.id).offset(self.offset).limit(self.limit)
        return {
            'count':self._total_page_count(),
            'next_page': self._get_next_page(),
            'previous_page': self._get_previous_page(),
            'data':data
        }
    



def get_currenct_date():
    
    # Specify the location
    location = "Baku, Azerbaijan"

    # Get the timezone for Baku
    timezone = pytz.timezone(pytz.country_timezones['AZ'][0])

    # Get the current date and time with timezone awareness
    now = datetime.datetime.now()
    aware_now = timezone.localize(now)

    formatted_time = aware_now.strftime("%Y-%m-%d")
    return formatted_time