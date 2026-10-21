import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import Category, Post, User


@pytest.fixture
def app(tmp_path):
    application = create_app(
        {
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "TESTING": True,
            "DEBUG": False,
            "WTF_CSRF_ENABLED": True,
            "UPLOAD_FOLDER": str(tmp_path / "media"),
            "MAX_CONTENT_LENGTH": 1024 * 1024,
            "POSTS_PER_PAGE": 2,
        }
    )
    with application.app_context():
        db.drop_all()
        db.create_all()
        user = User(name="Admin", username="admin", email="admin@example.test")
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
            post = Post()
            post.title = f"Post {number}"
            post.alias = f"post-{number}"
            post.category_id = category.id
            post.textbody = "<p>Post body</p>"
            db.session.add(post)
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
