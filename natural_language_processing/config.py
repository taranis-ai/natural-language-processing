from typing import Literal
from taranis_base_bot.config import CommonSettings


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


Config = Settings()
