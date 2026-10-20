from flask import g
from app.infrastructure.repositories.category import CategoryRepository
from app.services.post import PostService
from app.infrastructure.repositories.post import PostRepository


def get_post_service():
    post_repo = PostRepository(g.db)
    category_repo = CategoryRepository(g.db)
    return PostService(post_repo, category_repo)
