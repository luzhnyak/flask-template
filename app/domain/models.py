# app/domain/models.py
from pydantic import BaseModel
from datetime import datetime
import re


class Post(BaseModel):
    id: int
    title: str
    slug: str
    comtent: int
    created_at: datetime

    @property
    def desc(self):
        text = self.textbody.replace("&nbsp;", " ").replace("\n", " ")
        cleanr = re.compile("<.*?>")
        return re.sub(cleanr, "", text)

    # def add_hit(self):
    #     if self.hits is not None:
    #         self.hits += 1
    #     else:
    #         self.hits = 1
    #     db.session.commit()


class Category(BaseModel):
    id: int
    name: str
    slug: str
    icon = str

    created_at: datetime


class Image(BaseModel):
    id: int
    title: str
    slug: str
    comtent: int
    created_at: datetime


class User(BaseModel):
    id: int
    title: str
    slug: str
    comtent: int
    created_at: datetime
