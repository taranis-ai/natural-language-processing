from gliner import GLiNER
from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor


class GLiNERModel(Predictor):
    model_name = "selfconstruct3d/AITSecNER"

    def __init__(self):
        self.model = GLiNER.from_pretrained("selfconstruct3d/AITSecNER", load_tokenizer=True)
        self.labels = ["CLICommand/CodeSnippet", "CON", "DATE", "GROUP", "LOC", "MALWARE", "ORG", "SECTOR", "TACTIC", "TECHNIQUE", "TOOL"]

    def predict(self, text: str, extended_output: bool = False) -> dict[str, str] | list[dict]:
        entities = self.model.predict_entities(text, self.labels, threshold=Config.confidence_threshold)
        if not entities:
            return {}

        if extended_output:
            out_list = []
            out_list.extend(
                {
                    "value": entity.get("text", ""),
                    "type": entity.get("label", ""),
                    "probability": entity.get("score", 0.0),
                    "position": f"{entity.get('start', '')}-{entity.get('end', '')}",
                }
                for entity in entities
                if isinstance(entity, dict) and entity.get("score", 0) > Config.confidence_threshold and entity.get("text") is not None
            )
            return out_list

        return {
            entity["text"]: entity.get("label", "")
            for entity in entities
            if isinstance(entity, dict) and entity.get("score", 0) > Config.confidence_threshold and entity.get("text") is not None
        }
