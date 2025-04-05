from flask import Flask
from flask_login import LoginManager

from config import config
from app.infrastructure.database import Base, async_engine
from app.presentation.views import views_bp
from app.presentation.auth import auth_bp
from app.presentation.admin import init_admin

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.secret_key = config.SECRET_KEY
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    # @app.before_serving
    # async def init_db():
    #     async with async_engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all)
    #         print("✅ Таблиці створено!")

    init_admin(app)  # 📌 Підключаємо Flask-Admin

    @app.context_processor
    def inject_constants():
        return {
            "MENU_ITEMS": config.MENU_ITEMS,
        }

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)

    return app
