from flask_admin.contrib.sqla import ModelView
# from flask_admin import form
from flask import flash, redirect, url_for, session, request
import flask_login as login
from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_admin import expose
# from jinja2 import Markup
# import requests
# import re
import utilites

# from config import Config
from app import db, app
from models import Article, Users, Category, Images


# ==================================================== View Models Admin
# Create customized model view class
class MyModelView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        articles = Article.query
        return self.render('admin/index.html', ARTICLES=articles, Article=Article, db=db)


class ArticlesView(ModelView):

    edit_template = 'admin/edit_article.html'
    create_template = 'admin/edit_article.html'
    # page_size = 50  # the number of entries to display on the list view
    column_exclude_list = ['textbody']
    form_widget_args = {
        'textbody': {
            'rows': 25,
            'class': 'form-control wysiwyg'
        }
    }

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
        return self._change_alias(
            super(ArticlesView, self).edit_form(obj)
        )

    def create_form(self, obj=None):
        return self._change_alias(
            super(ArticlesView, self).create_form(obj)
        )


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(Users).get(user_id)


# Initialize flask-login
init_login()


# admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin = Admin(app, name='Admin Panel', index_view=MyAdminIndexView(), template_mode='bootstrap3')
admin.add_view(ArticlesView(Article, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Images, db.session))
