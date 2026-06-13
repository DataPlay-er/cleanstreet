# Settings: DB URL, Redis URL, model paths

from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache

class Settings(BaseSettings):

    # PostgreSQL URL:
    database_url: str

    # redis url:
    redis__url: "redis://localhost:6379/0"

    # models path
     


settings = Settings()    