from config import config
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

async_engine = create_async_engine(
    config.DATABASE_URL_ASYNC, echo=True, poolclass=NullPool
)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(config.DATABASE_URL_SYNC, echo=True)
sync_session = sessionmaker(bind=sync_engine)


class Base(DeclarativeBase):
    pass


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
