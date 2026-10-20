from app.infrastructure.index import Category
from app.utils.repository import SQLAlchemyRepository


class CategoryRepository(SQLAlchemyRepository):
    model = Category
