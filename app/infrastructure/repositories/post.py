from app.infrastructure.models import Post
from app.utils.repository import SQLAlchemyRepository


class PostRepository(SQLAlchemyRepository):
    model = Post
