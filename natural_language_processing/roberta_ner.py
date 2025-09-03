from transformers import pipeline
from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor


class RobertaNER(Predictor):
    model_name = "xlm-roberta-large-finetuned-conll03-english"

    def __init__(self):
        self.model = pipeline(task="ner", model=self.model_name, aggregation_strategy="simple")

    def predict(self, text: str, extended_output: bool = False, is_cybersecurity: bool = False) -> dict[str, str] | list[dict]:
        entities = self.model(text)
        if not entities:
            return {}

        if extended_output:
            out_list = []
            out_list.extend(
                {
                    "value": entity.get("word", ""),
                    "type": entity.get("entity_group", ""),
                    "probability": float(entity.get("score", 0.0)),
                    "position": f"{entity.get('start', '')}-{entity.get('end', '')}",
                }
                for entity in entities
                if isinstance(entity, dict) and entity.get("score", 0) > Config.confidence_threshold and entity.get("word") is not None
            )
            return out_list

        return {
            entity["word"]: entity["entity_group"]
            for entity in entities
            if isinstance(entity, dict) and entity.get("score", 0) > Config.confidence_threshold and entity.get("word") is not None
        }
