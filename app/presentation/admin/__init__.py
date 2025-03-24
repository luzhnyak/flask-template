from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

from app.infrastructure.database import db
from app.infrastructure.models import Posts, Users, Category, Images
from app.presentation.admin.views import MyAdminIndexView, PostsView


admin = Admin(name='Admin Panel',
              index_view=MyAdminIndexView(), template_mode='bootstrap3')


def init_admin(app):
    admin.init_app(app)

    admin.add_view(PostsView(Posts, db.session))
    admin.add_view(ModelView(Category, db.session))
    admin.add_view(ModelView(Images, db.session))
