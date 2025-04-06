# app/application/services.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.domain.models import Category
from app.infrastructure.repositories.category import CategoryRepository

class CategoryService:
    
    async def __init__(self, db: AsyncSession):
        self.category_repo = CategoryRepository(db)      
    

    async def get_all_categories(self) -> List[Category]:
        return await self.category_repo.find_all()

    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        return await self.category_repo.find_one(id=category_id)

    async def create_category(self, title: str, slug:str, content: str) -> Category:
        new_category = Category(title=title, content=content, slug=slug)
        return await self.category_repo.add_one(new_category)

    async def update_category(self, category_id: int, title: str, slug:str, content: str) -> Optional[Category]:
        existing_category = await self.get_category_by_id(category_id)
        if not existing_category:
            return None
        updated_category = Category(id=category_id, title=title, slug=slug, content=content)
        return await self.category_repo.edit_one(category_id, updated_category)

    async def delete_category(self, category_id: int) -> bool:
        return await self.category_repo.delete_one(category_id)
