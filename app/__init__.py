from flask import Flask
from flask_login import LoginManager

from app.infrastructure.models import User
from config import config
from app.infrastructure.database import db
from app.presentation.views import views_bp
from app.presentation.auth import auth_bp
from app.presentation.admin import init_admin

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    print("DATABASE_URL", config.DATABASE_URL)

    app.secret_key = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("Таблиці створено!")

    login_manager.init_app(app)
    # login_manager.login_view = "auth.login"  # 📌 Де знаходиться сторінка логіну
    # login_manager.login_message = "Будь ласка, увійдіть, щоб отримати доступ до адмінки."

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

    init_admin(app)  # 📌 Підключаємо Flask-Admin

    @app.context_processor
    def inject_constants():
        return {
            "MENU_ITEMS": [],
        }

    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)

    return app
