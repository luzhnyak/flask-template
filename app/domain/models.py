# app/domain/models.py
from pydantic import BaseModel
from datetime import datetime


class Post(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
