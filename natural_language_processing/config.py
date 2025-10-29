from typing import Literal
from taranis_base_bot.config import CommonSettings


class Settings(CommonSettings):
    MODEL: Literal["gliner", "flair", "roberta", "roberta_german"] = "gliner"
    PACKAGE_NAME: str = "natural_language_processing"
    HF_MODEL_INFO: bool = True
    PAYLOAD_KEY: str = "text"
    CONFIDENCE_THRESHOLD: float = 0.9


Config = Settings()
