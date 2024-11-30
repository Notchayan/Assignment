from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    mongo_connection_string: str
    database_name: str
    api_port: int
    environment: str
    log_level: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
