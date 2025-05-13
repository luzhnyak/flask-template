from app.services.user import UserService
from flask import Flask, g

from config import config
from app.infrastructure.database import Async_session, Base, async_engine, sync_session
from app.presentation.views import views_bp
from app.presentation.auth import auth_bp
from app.presentation.admin import init_admin


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблиці створено!")


def create_app():
    app = Flask(__name__)

    app.secret_key = config.SECRET_KEY
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    init_admin(app)

    @app.before_request
    def create_session():
        g.db = Async_session()

    @app.teardown_request
    def remove_session(exception=None):
        Async_session.remove()

    @app.context_processor
    def inject_constants():
        return {
            "MENU_ITEMS": config.MENU_ITEMS,
        }

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)

    return app
