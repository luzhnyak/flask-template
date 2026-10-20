import os
import dotenv

dotenv.load_dotenv()


class Config(object):
    DEBUG = os.getenv("DEBUG")
    DOMEN = os.getenv("DOMEN")
    SECRET_KEY = os.getenv("SECRET_KEY")

    GOOGLE_RECAPTCHA_SITE_KEY = os.getenv("GOOGLE_RECAPTCHA_SITE_KEY")

    ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

    APP_FOLDER = os.getenv("APP_FOLDER")
    IMAGES_FOLDER = os.path.join("static", "img")
    FULL_IMAGES_FOLDER = os.path.join(APP_FOLDER, IMAGES_FOLDER)
