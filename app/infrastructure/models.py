from flask import flash, redirect, url_for, session
from functools import wraps


from app.infrastructure.database import db


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Please login", "danger")
            return redirect(url_for("login"))

    return wrap


class BaseModel(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )


class Post(BaseModel):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    slug = db.Column(db.String())
    content = db.Column(db.Text())
    main_image = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

    category = db.relationship("Category")


class Category(BaseModel):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String())
    slug = db.Column(db.String())
    icon = db.Column(db.String())


class Image(BaseModel):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))
    type = db.Column(db.Unicode(4))
    post_id = db.Column(db.Integer)


class User(BaseModel):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.String())

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

    def __repr__(self):
        return "<User ('%s')>" % (self.username)
