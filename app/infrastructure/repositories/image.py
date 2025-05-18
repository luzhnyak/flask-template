from app.infrastructure.index import Image
from app.utils.repository import SQLAlchemyRepository


class ImageRepository(SQLAlchemyRepository):
    model = Image
