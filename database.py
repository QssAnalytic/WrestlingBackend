from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings


engine = create_engine(
    url= settings.DATABASE_URL_psycopg,
    echo=True
)

session_factory = sessionmaker(engine)


def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    ...