# app/infrastructure/database.py
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# db = SQLAlchemy()
import logging


from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


logger = logging.getLogger(__name__)

DATABASE_URL_ASYNC = (
    "postgresql+asyncpg://postgres:oleg010682@localhost:5432/flask_start"
)
DATABASE_URL_SYNC = "postgresql://postgres:oleg010682@localhost:5432/flask_start"

async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True, poolclass=NullPool)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(DATABASE_URL_SYNC, echo=True)
sync_session = sessionmaker(bind=sync_engine)


class Base(DeclarativeBase):
    pass


# Dependency для отримання сесії


# async def get_session() -> AsyncSession:
#     async with async_session() as session:
#         yield session
#         await session.commit()


@asynccontextmanager
async def get_sync_session():
    try:
        async with sync_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_session():
    try:
        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
