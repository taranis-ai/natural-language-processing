from typing import Literal
from taranis_base_bot.config import CommonSettings
from pydantic import ValidationInfo, field_validator


class Settings(CommonSettings):
    MODEL: Literal["gliner", "roberta", "roberta_german"] = "gliner"
    PACKAGE_NAME: str = "natural_language_processing"
    HF_MODEL_INFO: bool = True
    GENERAL_TEXT_CHUNK_LENGTH: int = 4000
    GENERAL_TEXT_CHUNK_OVERLAP: int = 200
    CYBERSEC_TEXT_CHUNK_LENGTH: int = 1200
    CYBERSEC_TEXT_CHUNK_OVERLAP: int = 200
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
    DBPEDIA_URI_OUTPUT: bool = False

    @field_validator("CONFIDENCE_THRESHOLD", mode="after")
    @classmethod
    def check_between_0_and_1(cls, v: float, info: ValidationInfo) -> float:
        if not isinstance(v, float) or v <= 0. or v >= 1.:
            raise RuntimeError("CONFIDENCE_THRESHOLD must be a number > 0 and < 1")
        return v

    @field_validator("GENERAL_TEXT_CHUNK_LENGTH", "CYBERSEC_TEXT_CHUNK_LENGTH", mode="after")
    @classmethod
    def check_text_chunk_length(cls, v: int, info: ValidationInfo) -> int:
        if not isinstance(v, int) or v <= 0:
            raise RuntimeError(f"{info.field_name} must be an integer > 0")
        return v

    @field_validator("GENERAL_TEXT_CHUNK_OVERLAP", "CYBERSEC_TEXT_CHUNK_OVERLAP", mode="after")
    @classmethod
    def check_text_chunk_overlap(cls, v: int, info: ValidationInfo) -> int:
        if not isinstance(v, int) or v < 0:
            raise RuntimeError(f"{info.field_name} must be an integer >= 0")
        return v


Config = Settings()
