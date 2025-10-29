from typing import Literal
from taranis_base_bot.config import CommonSettings


class Settings(CommonSettings):
    MODEL: Literal["gliner", "flair", "roberta", "roberta_german"] = "gliner"
    PACKAGE_NAME: str = "natural_language_processing"
    HF_MODEL_INFO: bool = True
    PAYLOAD_SCHEMA: dict[str, dict] = {
        "text": {"type": "str", "required": True},
        "extended_output": {"type": "bool", "required": False},
        "is_cybersecurity": {"type": "bool", "required": False},
    }
    CONFIDENCE_THRESHOLD: float = 0.7


Config = Settings()
