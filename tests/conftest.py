import pytest
from app import create_app
from app.infrastructure.models import User  # Приклад моделі
from app.infrastructure.database import db  # Приклад БД


@pytest.fixture
def app():
    """Фікстура для створення тестового застосунку Flask"""
    app = create_app(testing=True)  # Створення застосунку в тестовому режимі
    with app.app_context():
        db.create_all()  # Створюємо таблиці в тестовій БД
        yield app
        db.session.remove()
        db.drop_all()  # Видаляємо таблиці після тестів


@pytest.fixture
def client(app):
    """Фікстура для клієнта тестового застосунку"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Фікстура для виконання команд CLI"""
    return app.test_cli_runner()
