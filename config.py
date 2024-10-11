import os
import dotenv
dotenv.load_dotenv()


class Config(object):
    DOMEN = os.getenv('DOMEN')
    SECRET_KEY = os.getenv('SECRET_KEY')

    # administrator list
    ADMINS = ['oleg.luzhnyak@gmail.com']

    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    # Folder
    APP_FOLDER = os.getenv('APP_FOLDER')
    IMAGES_FOLDER = os.path.join("static", "img")
    FULL_IMAGES_FOLDER = os.path.join(APP_FOLDER, IMAGES_FOLDER)
