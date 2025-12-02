from typing import Literal
from taranis_base_bot.config import CommonSettings
from pydantic import ValidationInfo, field_validator


class Settings(CommonSettings):
    MODEL: Literal["gliner", "roberta", "roberta_german"] = "gliner"
    PACKAGE_NAME: str = "natural_language_processing"
    HF_MODEL_INFO: bool = True
    PAYLOAD_SCHEMA: dict[str, dict] = {
        "text": {"type": "str", "required": True},
        "extended_output": {"type": "bool", "required": False},
        "cybersecurity": {"type": "bool", "required": False},
    }
    CONFIDENCE_THRESHOLD: float = 0.7
    ENTITIES: list = [
        "Person",
        "Location",
        "Organization",
        "Product",
        "Address",
        "CLICommand/CodeSnippet",
        "Con",
        "Group",
        "Malware",
        "Sector",
        "Tactic",
        "Technique",
        "Tool",
        "Misc",
    ]
    DBPEDIA_URL: str = "https://lookup.dbpedia.org/api/search"
    DBPEDIA_LOOKUP: bool = False

    @field_validator("CONFIDENCE_THRESHOLD", mode="after")
    @classmethod
    def check_between_0_and_1(cls, v: float, info: ValidationInfo) -> float:
        if not isinstance(v, float) or v <= 0. or v >= 1.:
            raise RuntimeError("CONFIDENCE_THRESHOLD must be a number > 0 and < 1")
        return v


Config = Settings()
