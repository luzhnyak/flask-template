from typing import ClassVar

from flask import redirect, request, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy.orm import joinedload
from wtforms.validators import DataRequired, ValidationError

from extensions import db
from models import Category, Image, Post
from utils import transliterate


class AdminAccess:
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.login", next=request.path))


class MyModelView(AdminAccess, ModelView):
    # Use Flask-WTF's token format for both model and action forms.
    form_base_class = FlaskForm
    page_size = 20


class MyAdminIndexView(AdminAccess, AdminIndexView):
    @expose("/")
    def index(self):
        posts = db.select(Post).options(joinedload(Post.category))
        popular = db.session.scalars(
            posts.order_by(Post.hits.desc(), Post.id.desc()).limit(10)
        ).all()
        recent = db.session.scalars(posts.order_by(Post.id.desc()).limit(10)).all()
        return self.render("admin/index.html", popular=popular, recent=recent)


class PostsView(MyModelView):
    edit_template = "admin/edit_post.html"
    create_template = "admin/create_post.html"
    column_exclude_list = ("textbody",)
    column_searchable_list = ("title",)
    column_default_sort = ("id", True)
    form_columns = ("category", "title", "alias", "textbody", "main_image")
    form_args: ClassVar[dict] = {
        "title": {"validators": [DataRequired()]},
        "category": {"validators": [DataRequired()]},
    }
    form_widget_args: ClassVar[dict] = {"textbody": {"rows": 25}}

    def on_model_change(self, form, model, is_created):
        model.alias = transliterate(model.alias or model.title)
        if not model.alias:
            raise ValidationError("Enter a valid alias or title.")
        with db.session.no_autoflush:
            duplicate = db.session.scalar(
                db.select(Post.id).where(
                    Post.alias == model.alias,
                    Post.category_id == model.category.id,
                    Post.id != model.id if model.id is not None else True,
                )
            )
        if duplicate is not None:
            raise ValidationError("This category already contains an post with that alias.")


class CategoriesView(MyModelView):
    form_args: ClassVar[dict] = {"name": {"validators": [DataRequired()]}}

    def on_model_change(self, form, model, is_created):
        model.alias = transliterate(model.alias or model.name)
        if not model.alias or model.alias in {
            "admin",
            "login",
            "logout",
            "search",
            "static",
            "media",
            "favicon-ico",
        }:
            raise ValidationError("Choose a non-reserved category alias.")
        with db.session.no_autoflush:
            duplicate = db.session.scalar(
                db.select(Category.id).where(
                    Category.alias == model.alias,
                    Category.id != model.id if model.id is not None else True,
                )
            )
        if duplicate is not None:
            raise ValidationError("A category with this alias already exists.")

    def on_model_delete(self, model):
        if (
            db.session.scalar(db.select(Post.id).where(Post.category_id == model.id).limit(1))
            is not None
        ):
            raise ValidationError("Move or delete this category's posts first.")


class ImageView(MyModelView):
    # File paths are created only by the validated upload endpoint.
    can_create = False
    can_edit = False
    can_delete = False


def init_admin(app):
    admin = Admin(
        app,
        name="Admin Panel",
        index_view=MyAdminIndexView(),
        theme=Bootstrap4Theme(swatch="cerulean"),
    )
    admin.add_view(PostsView(Post, db))
    admin.add_view(CategoriesView(Category, db))
    admin.add_view(ImageView(Image, db))
