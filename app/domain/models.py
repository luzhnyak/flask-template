from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
import re


class Post(BaseModel):
    id: int
    title: str
    slug: str
    content: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Category(BaseModel):
    id: int
    name: str
    slug: str
    icon: str

    model_config = ConfigDict(from_attributes=True)


class Image(BaseModel):
    id: int
    name: str
    path: str
    type: int

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
