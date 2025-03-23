from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Config(BaseSettings):
    DOMEN: str = "http://localhost:5000"
    DATABASE_URL: str = "sqlite:///db.sqlite3"
    SECRET_KEY: str = "your_default_secret_key"
    DEBUG: bool = True

    APP_FOLDER: str

    @property
    def ALLOWED_EXTENSIONS(self) -> set:
        return set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    @property
    def IMAGES_FOLDER(self) -> str:
        return os.path.join("static", "img")

    @property
    def FULL_IMAGES_FOLDER(self) -> str:
        return os.path.join(self.APP_FOLDER, self.IMAGES_FOLDER)

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


config = Config()
