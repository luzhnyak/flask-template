from app.infrastructure.index import Post
from app.utils.repository import SQLAlchemyRepository


class PostRepository(SQLAlchemyRepository):
    model = Post
