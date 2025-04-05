# app/infrastructure/database.py
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL_ASYNC = "postgresql+asyncpg://postgres:postgres@localhost:5432/flask_start"
DATABASE_URL_SYNC = "postgresql://user:pass@localhost/db"

async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(DATABASE_URL_SYNC, echo=True)
sync_session = sessionmaker(bind=sync_engine)


class Base(DeclarativeBase):
    pass


# Dependency для отримання сесії
async def get_session() -> AsyncSession:  # type: ignore
    async with async_session() as session:
        yield session
