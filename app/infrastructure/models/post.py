from functools import wraps
from datetime import datetime
from flask import flash, redirect, url_for, session
from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.database import Base
from app.infrastructure.models.base import BaseModel


class Post(BaseModel):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100))
    content: Mapped[str]
    main_image: Mapped[str]
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship("Category", back_populates="posts")


class Category(BaseModel):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(100))

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category")
