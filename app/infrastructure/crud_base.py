from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Type, TypeVar, Generic

ModelType = TypeVar("ModelType")


class BaseCRUD(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_all(self, db: AsyncSession):
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, obj_id: int):
        result = await db.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: dict):
        obj = self.model(**obj_in)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, obj_id: int, obj_in: dict):
        await db.execute(
            update(self.model).where(self.model.id == obj_id).values(**obj_in)
        )
        await db.commit()

    async def delete(self, db: AsyncSession, obj_id: int):
        await db.execute(delete(self.model).where(self.model.id == obj_id))
        await db.commit()
