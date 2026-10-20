import re
from html import unescape

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    title = db.Column(db.String())
    alias = db.Column(db.String())
    textbody = db.Column(db.Text())
    main_image = db.Column(db.String())
    hits = db.Column(db.Integer, default=0)
    category = db.relationship("Category")

    @property
    def desc(self):
        return " ".join(unescape(re.sub(r"<[^>]*>", "", self.textbody or "")).split())

    def add_hit(self):
        # Increment atomically so concurrent requests do not lose views.
        db.session.execute(
            db.update(Article)
            .where(Article.id == self.id)
            .values(hits=db.func.coalesce(Article.hits, 0) + 1)
        )
        db.session.commit()

    def __repr__(self):
        return self.title or "Article"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    alias = db.Column(db.String())
    textbody = db.Column(db.Text())
    icon = db.Column(db.String())

    def __repr__(self):
        return self.name or "Category"


class Images(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))
    type = db.Column(db.Unicode(4))
    create_date = db.Column(db.String())
    article_id = db.Column(db.Integer)


class Users(UserMixin, db.Model):
    # Every account in this starter is an admin; there is no public registration.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    fb_id = db.Column(db.Integer())
    google_id = db.Column(db.Integer())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        # Old plaintext passwords are intentionally not accepted.
        if not self.password:
            return False
        try:
            return check_password_hash(self.password, password)
        except ValueError:
            return False

    def __repr__(self):
        return self.username or "User"
