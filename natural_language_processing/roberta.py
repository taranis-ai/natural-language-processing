from transformers import pipeline
from natural_language_processing.config import Config
from natural_language_processing.post_process import map_entity_types, is_entity_allowed


class Roberta:
    model_name = "xlm-roberta-large-finetuned-conll03-english"

    def __init__(self):
        self.model = pipeline(task="ner", model=self.model_name, aggregation_strategy="simple")

    def predict(self, text: str, extended_output: bool = False) -> dict[str, str] | list[dict]:
        entities = self.model(text)
        if not entities:
            return {}

        if extended_output:
            out_list = []
            out_list.extend(
                {
                    "value": entity.get("word", ""),
                    "type": map_entity_types(entity.get("entity_group", "")),
                    "probability": float(entity.get("score", 0.0)),
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
            and is_entity_allowed(map_entity_types(entity.get("entity_group", "")), Config.ENTITIES)
        }
