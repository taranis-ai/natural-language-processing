from transformers import pipeline
from natural_language_processing.config import Config
from natural_language_processing.post_process import map_entity_types, is_entity_allowed
from natural_language_processing.ioc_finder import extract_ioc

class RobertaGerman:
    model_name = "xlm-roberta-large-finetuned-conll03-german"

    def __init__(self):
        self.model = pipeline(task="ner", model=self.model_name, aggregation_strategy="simple")

    def predict(self, text: str, extended_output: bool = False) -> dict[str, str] | list[dict]:
        entities = self.model(text)
        ioc = extract_ioc(text)
        ioc = [{**e,
                "word": e.get("ioc", ""),
                "entity_group": e.get("type", ""),
               }
               for e in ioc
        ]
        entities = entities + ioc
        if not entities:
            return [] if extended_output else {}

        if extended_output:
            out_list = []
            out_list.extend(
                {
                    "value": entity.get("word", ""),
                    "type": map_entity_types(entity.get("entity_group", "")),
                    "probability": round(float(entity.get("score", 0.0)), 2),
                    "position": f"{entity.get('start', '')}-{entity.get('end', '')}",
                }
                for entity in entities
                if isinstance(entity, dict)
                and entity.get("score", 0) > Config.CONFIDENCE_THRESHOLD
                and entity.get("word") is not None
                and is_entity_allowed(map_entity_types(entity.get("entity_group", "")), Config.ENTITIES)
            )
            return out_list

        return {
            entity["word"]: map_entity_types(entity["entity_group"])
            for entity in entities
            if isinstance(entity, dict)
            and entity.get("score", 0) > Config.CONFIDENCE_THRESHOLD
            and entity.get("word") is not None
            and is_entity_allowed(map_entity_types(entity["entity_group"]), Config.ENTITIES)
        }
