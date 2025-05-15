from flask import g
from app.infrastructure.repositories.image import ImageRepository
from app.services.image import ImageService


def get_image_service():
    image_repo = ImageRepository(g.db)
    return ImageService(image_repo)
