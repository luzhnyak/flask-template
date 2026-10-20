from app.infrastructure.index import User
from app.utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User
