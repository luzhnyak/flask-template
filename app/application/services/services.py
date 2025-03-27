# app/application/services.py
from typing import List, Optional
from app.domain.models import Post
from app.domain.interfaces import IPostRepository


class PostService:
    def __init__(self, post_repo: IPostRepository):
        self.post_repo = post_repo

    def get_all_posts(self) -> List[Post]:
        return self.post_repo.get_all_posts()

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return self.post_repo.get_post_by_id(post_id)

    def create_post(self, title: str, content: str, author_id: int) -> Post:
        new_post = Post(id=0, title=title, content=content,
                        author_id=author_id, created_at=None)
        return self.post_repo.create_post(new_post)

    def update_post(self, post_id: int, title: str, content: str) -> Optional[Post]:
        existing_post = self.post_repo.get_post_by_id(post_id)
        if not existing_post:
            return None
        updated_post = Post(id=post_id, title=title, content=content,
                            author_id=existing_post.author_id, created_at=existing_post.created_at)
        return self.post_repo.update_post(post_id, updated_post)

    def delete_post(self, post_id: int) -> bool:
        return self.post_repo.delete_post(post_id)
