from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import  DeclarativeBase, sessionmaker

from config import settings



engine = create_async_engine(settings.DATABASE_URL_aync_psycopg, echo=True)
async_session_factory = async_sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine,
)


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# def get_db():
#     db = async_session_factory()
#     try:
#         yield db
#     finally:
#         db.close()


class Base(DeclarativeBase):
    ...


# session_factory = sessionmaker(engine)

# engine = create_engine(
#     url= settings.DATABASE_URL_psycopg,
#     # echo=True
# )