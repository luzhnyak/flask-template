from flask import flash, redirect, url_for, session, request
from functools import wraps
import re

from app import db


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


class Article(db.Model):
    def __init__(self):
        self.title = "title"

    def __repr__(self):
        return "<Article('%s')>" % (self.title)

    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    title = db.Column(db.String())
    alias = db.Column(db.String())
    textbody = db.Column(db.Text())
    main_image = db.Column(db.String())
    hits = db.Column(db.Integer)

    category = db.relationship('Category')

    @property
    def desc(self):

        text = self.textbody.replace("&nbsp;", " ").replace("\n", " ")
        cleanr = re.compile('<.*?>')
        return re.sub(cleanr, '', text)

    def add_hit(self):
        if self.hits is not None:
            self.hits += 1
        else:
            self.hits = 1
        db.session.commit()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String())
    alias = db.Column(db.String())
    textbody = db.Column(db.Text())
    icon = db.Column(db.String())

    def __init__(self):
        self.name = "name"

    def __repr__(self):
        return self.name


class Images(db.Model):
    __tablename__ = 'images'

    def __init__(self, name, path, type, create_date, article_id):

        self.name = name
        self.path = path
        self.type = type
        self.create_date = create_date
        self.article_id = article_id

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))
    type = db.Column(db.Unicode(4))
    create_date = db.Column(db.String())
    article_id = db.Column(db.Integer)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String())
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    fb_id = db.Column(db.Integer())
    google_id = db.Column(db.Integer())

    def __init__(self, name, username, email):
        self.name = name
        self.username = username
        self.email = email

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
