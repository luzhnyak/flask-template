import pytest
from app import create_app
from app.infrastructure.index import Users
from app.infrastructure.database import db


@pytest.fixture(scope="session")
def app():
    app = create_app()
    with app.app_context():
        app.config.update(
            {
                "TESTING": True,
            }
        )
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
