from pydantic import field_validator, ValidationInfo, BaseModel
from pydantic_settings import BaseSettings
from datetime import datetime
from typing import Literal


class ExtendedNerOutput(BaseModel):
    value: str
    type: str
    probability: float
    position: str


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
    MODEL: Literal["flair", "roberta", "roberta_german", "gliner"] = "flair"
    EXT_OUT: bool = False

    confidence_threshold: float = 0.9

    @field_validator("API_KEY", mode="before")
    def check_non_empty_string(cls, v: str, info: ValidationInfo) -> str:
        if not isinstance(v, str) or not v.strip():
            print("API_KEY is not set or empty, disabling API key requirement")
        return v


Config = Settings()
