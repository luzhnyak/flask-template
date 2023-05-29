from app import db
from flask_admin.contrib.sqla import ModelView
# from flask_admin import form
from flask import flash, redirect, url_for, session, request
from functools import wraps
import flask_login as login
from flask_admin import AdminIndexView
from flask_admin import expose
# from jinja2 import Markup
import requests
import re
import utilites
from config import Config


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

    def is_authenticated(self):
        return True


# ==================================================== View Models Admin
# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        if login.current_user.is_authenticated:
            return login.current_user.role_id == 1
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
        # COMENTS = Coments.query.filter_by(user_id=login.current_user.id)
        # form = ComentsForm(request.form)
        # if request.method == 'POST' and form.validate():
        # 	coment = Coments.query.filter_by(id=int(form.id.data)).first()
        # 	coment.coment = form.message.data
        # 	adb.session.commit()

        # 	flash('Коментар змінено', 'success')
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
