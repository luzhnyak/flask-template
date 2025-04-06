# app/application/services.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.domain.models import Post
from app.infrastructure.repositories.post import PostRepository

class PostService:
    
    def __init__(self, db: AsyncSession):
        self.post_repo = PostRepository(db)      
    

    async def get_posts(self) -> List[Post]:
        return await self.post_repo.find_all(skip=0, limit=10)

    async def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return await self.post_repo.find_one(id=post_id)
    
    async def get_post_by_slug(self, slug: str) -> Optional[Post]:
        return await self.post_repo.find_one(slug=slug)

    async def create_post(self, title: str, slug:str, content: str) -> Post:
        new_post = Post(title=title, content=content, slug=slug)
        return await self.post_repo.add_one(new_post)

    async def update_post(self, post_id: int, title: str, slug:str, content: str) -> Optional[Post]:
        existing_post = await self.get_post_by_id(post_id)
        if not existing_post:
            return None
        updated_post = Post(id=post_id, title=title, slug=slug, content=content)
        return await self.post_repo.edit_one(post_id, updated_post)

    async def delete_post(self, post_id: int) -> bool:
        return await self.post_repo.delete_one(post_id)
