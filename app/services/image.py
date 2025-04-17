# app/application/services.py
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.domain.models import Image, Post
from app.infrastructure.repositories.image import ImageRepository
from app.infrastructure.repositories.post import PostRepository
from app.infrastructure.database import async_session


class ImageService:

    def __init__(self, db: AsyncSession):
        self.image_repo = ImageRepository(db)

    async def get_images_by_post_id(self, post_id) -> List[Image]:
        return await self.image_repo.find_all(post_id=post_id, skip=0, limit=10)

    async def get_image_by_id(self, image_id: int) -> Optional[Image]:
        return await self.image_repo.find_one(id=image_id)

    async def create_image(self, name: str, path: str, type: int) -> Image:
        new_image = Image(name=name, path=path, type=type)
        return await self.image_repo.add_one(new_image)

    async def delete_image(self, image_id: int) -> bool:
        return await self.image_repo.delete_one(image_id)


@asynccontextmanager
async def get_image_service() -> ImageService:  # type: ignore
    async with async_session() as session:
        yield ImageService(session)
