from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

from app.infrastructure.database import db
from app.infrastructure.models import Post, User, Category, Image
from app.presentation.admin.views import MyAdminIndexView, PostsView


admin = Admin(
    name="Admin Panel", index_view=MyAdminIndexView(), template_mode="bootstrap3"
)


def init_admin(app):
    if not hasattr(app, "flask_admin_initialized"):
        admin.init_app(app)

        admin.add_view(PostsView(Post, db.session))
        admin.add_view(ModelView(Category, db.session))
        admin.add_view(ModelView(Image, db.session))

        app.flask_admin_initialized = True
