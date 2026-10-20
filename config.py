from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Config(BaseSettings):
    DOMEN: str = "http://localhost:5000"
    SECRET_KEY: str = "your_default_secret_key"
    DEBUG: bool = True
    APP_FOLDER: str

    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "oleg010682"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "flask_start"

    @property
    def DATABASE_URL_ASYNC(self):
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def DATABASE_URL_SYNC(self):
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def ALLOWED_EXTENSIONS(self) -> set:
        return set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

    @property
    def IMAGES_FOLDER(self) -> str:
        return os.path.join("static", "img")

    @property
    def FULL_IMAGES_FOLDER(self) -> str:
        return os.path.join(self.APP_FOLDER, self.IMAGES_FOLDER)

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @property
    def MENU_ITEMS(self):
        return [
            {"name": "Posts", "url": "/posts"},
        ]


config = Config()
