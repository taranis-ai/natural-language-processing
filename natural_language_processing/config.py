from pydantic import BaseSettings
from datetime import datetime

class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    MODULE_ID: str = "NLPBot"
    DEBUG: bool = False
    API_KEY: str = ""

    COLORED_LOGS: bool = True
    BUILD_DATE: datetime = datetime.now()
    GIT_INFO: dict[str, str] | None = None
    CACHE_TYPE: str = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT: int = 300

Config = Settings()
