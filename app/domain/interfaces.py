from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Post


class IPostRepository(ABC):
    @abstractmethod
    def get_all_posts(self) -> List[Post]:
        pass

    @abstractmethod
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        pass

    @abstractmethod
    def create_post(self, post: Post) -> Post:
        pass

    @abstractmethod
    def update_post(self, post_id: int, post: Post) -> Optional[Post]:
        pass

    @abstractmethod
    def delete_post(self, post_id: int) -> bool:
        pass
