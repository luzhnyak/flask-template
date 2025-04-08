# app/application/services.py
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.infrastructure.database import async_session
from app.domain.models import User
from app.infrastructure.repositories.user import UserRepository


class UserService:

    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def get_all_users(self) -> List[User]:
        return await self.user_repo.find_all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.user_repo.find_one(id=user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        user = await self.user_repo.find_one(email=email)
        return User.model_validate(user)

    async def create_user(self, title: str, slug: str, content: str) -> User:
        new_user = User(title=title, content=content, slug=slug)
        return await self.user_repo.add_one(new_user)

    async def update_user(
        self, user_id: int, title: str, slug: str, content: str
    ) -> Optional[User]:
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            return None
        updated_user = User(id=user_id, title=title, slug=slug, content=content)
        return await self.user_repo.edit_one(user_id, updated_user)

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repo.delete_one(user_id)


@asynccontextmanager
async def get_user_service() -> UserService:  # type: ignore
    async with async_session() as session:
        yield UserService(session)
