from functools import wraps
from datetime import datetime
from flask import flash, redirect, url_for, session
from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.infrastructure.database import Base
from app.infrastructure.models.base import BaseModel


class Image(BaseModel):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    path: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(4))
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))

    # posts: Mapped[list["Post"]] = relationship("Post", back_populates="images")
