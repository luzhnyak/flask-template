from config import config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session

async_engine = create_async_engine(
    config.DATABASE_URL_ASYNC, echo=True, poolclass=NullPool
)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(config.DATABASE_URL_SYNC, echo=True)
sync_session = sessionmaker(bind=sync_engine)
Async_session = scoped_session(async_session)


class Base(DeclarativeBase):
    pass
