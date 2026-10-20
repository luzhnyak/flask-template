from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFError

from config import Config
from extensions import csrf, db, login_manager


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config is not None:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY in .env before starting the application.")
    if bool(app.config.get("GOOGLE_RECAPTCHA_SITE_KEY")) != bool(
        app.config.get("GOOGLE_RECAPTCHA_SECRET_KEY")
    ):
        raise RuntimeError("Configure both reCAPTCHA keys, or leave both empty.")

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    from admin import init_admin
    from cli import register_commands
    from context import inject_constants
    from models import Users
    from views import bp

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(Users, int(user_id))
        except (TypeError, ValueError):
            return None

    app.register_blueprint(bp)
    app.context_processor(inject_constants)
    init_admin(app)
    register_commands(app)

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        if request.endpoint == "main.upload_file":
            return jsonify(uploaded=0, error={"message": "Invalid CSRF token."}), 400
        return render_template(
            "error.html", code=400, message="Форма застаріла. Оновіть сторінку й повторіть дію."
        ), 400

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="Сторінку не знайдено."), 404

    @app.errorhandler(413)
    def too_large(error):
        if request.endpoint == "main.upload_file":
            return jsonify(uploaded=0, error={"message": "File is too large."}), 413
        return render_template("error.html", code=413, message="Файл завеликий."), 413

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        # Flask-Login's template context can query the database. Keep the fallback
        # independent of templates so a database outage cannot break it again.
        return app.response_class("Внутрішня помилка сервера.", status=500, mimetype="text/plain")

    return app
