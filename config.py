import os
import dotenv
dotenv.load_dotenv()


class Config(object):
    DOMEN = os.getenv('DOMEN')
    SECRET_KEY = os.getenv('SECRET_KEY')

    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    APP_FOLDER = os.getenv('APP_FOLDER')
    IMAGES_FOLDER = os.path.join("static", "img")
    FULL_IMAGES_FOLDER = os.path.join(APP_FOLDER, IMAGES_FOLDER)
