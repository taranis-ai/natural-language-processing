from gliner import GLiNER
from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor


class GLiNERPPN(Predictor):
    model_name = "llinauer/gliner_ppn"

    def __init__(self):
        self.model = GLiNER.from_pretrained(self.model_name)
        self.labels = ["datetime", "event", "location", "organization", "person", "persontype"]

    def predict(self, text: str) -> dict[str, str]:
        if entities := self.model.predict_entities(text, self.labels, threshold=Config.confidence_threshold):
            return {
                entity["text"]: entity["label"].capitalize() for entity in entities if isinstance(entity, dict) and entity.get("score", 0)
            }

        return {}
