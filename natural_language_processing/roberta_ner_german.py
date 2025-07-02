from transformers import pipeline
from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor
from natural_language_processing.misc import get_word_positions


class RobertaGermanNER(Predictor):
    model_name = "xlm-roberta-large-finetuned-conll03-german"

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
                    "type": entity.get("entity_group", ""),
                    "confidence": float(entity.get("score", 0.0)),
                    "position": get_word_positions(text, entity.get("word", ""), entity.get("start", None)),
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
