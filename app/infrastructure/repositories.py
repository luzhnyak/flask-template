# app/infrastructure/repositories.py
from app.domain.interfaces import IPostRepository
from app.infrastructure.database import db
from app.infrastructure.models import Post as PostModel
from app.domain.models import Post
from typing import List, Optional


class PostRepository(IPostRepository):
    def get_all_posts(self) -> List[Post]:
        posts = db.session.query(PostModel).all()
        return [Post(id=p.id, title=p.title, content=p.content, author_id=p.author_id, created_at=p.created_at) for p in posts]

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        post = db.session.query(PostModel).filter_by(id=post_id).first()
        if post:
            return Post(id=post.id, title=post.title, content=post.content, author_id=post.author_id, created_at=post.created_at)
        return None

    def create_post(self, post: Post) -> Post:
        new_post = PostModel(
            title=post.title, content=post.content, author_id=post.author_id)
        db.session.add(new_post)
        db.session.commit()
        return Post(id=new_post.id, title=new_post.title, content=new_post.content, author_id=new_post.author_id, created_at=new_post.created_at)

    def update_post(self, post_id: int, post: Post) -> Optional[Post]:
        existing_post = db.session.query(
            PostModel).filter_by(id=post_id).first()
        if not existing_post:
            return None
        existing_post.title = post.title
        existing_post.content = post.content
        db.session.commit()
        return Post(id=existing_post.id, title=existing_post.title, content=existing_post.content, author_id=existing_post.author_id, created_at=existing_post.created_at)

    def delete_post(self, post_id: int) -> bool:
        post = db.session.query(PostModel).filter_by(id=post_id).first()
        if not post:
            return False
        db.session.delete(post)
        db.session.commit()
        return True
