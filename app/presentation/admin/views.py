from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
import flask_login as login
from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_admin import expose

import app.utils.utilites as utilites
from app.infrastructure.database import db
from app.infrastructure.models import Post, User, Category, Image

# ==================================================== View Models Admin
# Create customized model view class


class MyModelView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("views.login", next=request.url))
        # return redirect('/login')


# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("views.login", next=request.url))
        # return redirect('/login')

    @expose("/", methods=["GET", "POST"])
    def index(self):
        articles = Post.query
        return self.render("admin/index.html", ARTICLES=articles, Post=Post, db=db)


class PostsView(ModelView):

    edit_template = "admin/edit_article.html"
    create_template = "admin/edit_article.html"
    # page_size = 50  # the number of entries to display on the list view
    column_exclude_list = ["textbody"]
    form_widget_args = {"textbody": {"rows": 25, "class": "form-control wysiwyg"}}

    def _change_alias(self, _form):
        try:
            if _form.alias.data is None:
                _form.alias.data = utilites.transliterate(_form.title.data)
            else:
                _form.alias.data = utilites.transliterate(_form.alias.data)

        except Exception as ex:
            print(ex)

        return _form

    def edit_form(self, obj=None):
        return self._change_alias(super(PostsView, self).edit_form(obj))

    def create_form(self, obj=None):
        return self._change_alias(super(PostsView, self).create_form(obj))
