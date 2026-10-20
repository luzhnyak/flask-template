import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import Article, Category, Users


@pytest.fixture
def app(tmp_path):
    application = create_app(
        {
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "TESTING": True,
            "WTF_CSRF_ENABLED": True,
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
            "MAX_CONTENT_LENGTH": 1024 * 1024,
            "ARTICLES_PER_PAGE": 2,
        }
    )
    with application.app_context():
        db.drop_all()
        db.create_all()
        user = Users(name="Admin", username="admin", email="admin@example.test")
        user.password = generate_password_hash("correct-password")
        category = Category()
        category.name = "Fishing"
        category.alias = "fishing"
        other = Category()
        other.name = "Other"
        other.alias = "other"
        db.session.add_all([user, category, other])
        db.session.flush()
        for number in range(3):
            article = Article()
            article.title = f"Article {number}"
            article.alias = f"article-{number}"
            article.cat_id = category.id
            article.textbody = "<p>Article body</p>"
            db.session.add(article)
        db.session.commit()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated(client):
    with client.session_transaction() as session:
        session["_user_id"] = "1"
        session["_fresh"] = True
    return client
