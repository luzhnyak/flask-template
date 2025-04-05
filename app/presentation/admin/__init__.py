from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

from app.infrastructure.database import Base, sync_session
from app.infrastructure.models import Post, User, Category, Image
from app.presentation.admin.views import MyAdminIndexView, PostsView


admin = Admin(
    name="Admin Panel", index_view=MyAdminIndexView(), template_mode="bootstrap3"
)


def init_admin(app):
    if not hasattr(app, "flask_admin_initialized"):
        admin.init_app(app)

        admin.add_view(PostsView(Post, sync_session))
        admin.add_view(ModelView(Category, sync_session))
        admin.add_view(ModelView(Image, sync_session))

        app.flask_admin_initialized = True
