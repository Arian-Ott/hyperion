from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    JWT_SECRET: str
    HOST: str = "127.0.0.1"
    PORT: int = 2468
    DEBUG: bool = False
    MARIADB_USER: str = "hyperion"
    MARIADB_PASSWORD: str = "hyperion"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DATABASE: str = "hyperion"
    model_config = SettingsConfigDict(extra="ignore", env_file=".env")
    DROP_DB:bool = False 
    @property
    def db_url(self):
        return f"mysql+asyncmy://{self.MARIADB_USER}:{self.MARIADB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DATABASE}"
