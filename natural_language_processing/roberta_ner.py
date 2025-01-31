from transformers import pipeline
from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor


class RobertaNER(Predictor):
    model_name = "xlm-roberta-large-finetuned-conll03-english"

    def __init__(self):
        self.model = pipeline(task="ner", model=self.model_name, aggregation_strategy="simple")

    def predict(self, text: str) -> dict[str, str]:
        if entities := self.model(text):
            return {
                entity["word"]: entity["entity_group"]
                for entity in entities
                if isinstance(entity, dict) and entity.get("score", 0) > Config.confidence_threshold and entity.get("word") is not None
            }

        return {}
