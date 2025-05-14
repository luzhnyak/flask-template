from flask import g
from app.infrastructure.repositories.user import UserRepository
from app.services.user import UserService


def get_user_service():
    user_repo = UserRepository(g.db)
    return UserService(user_repo)
