from gliner import GLiNER
from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor
from natural_language_processing.misc import get_word_positions


class GLiNERModel(Predictor):
    model_name = "selfconstruct3d/AITSecNER"

    def __init__(self):
        self.model = GLiNER.from_pretrained("selfconstruct3d/AITSecNER", load_tokenizer=True)
        self.labels = ["CLICommand/CodeSnippet", "CON", "DATE", "GROUP", "LOC", "MALWARE", "ORG", "SECTOR", "TACTIC", "TECHNIQUE", "TOOL"]

    def predict(self, text: str) -> dict[str, str] | list[dict]:
        entities = self.model.predict_entities(text, self.labels, threshold=Config.confidence_threshold)
        if not entities:
            return {}

        if Config.EXT_OUT:
            out_list = []
            out_list.extend(
                {
                    "value": entity.get("text", ""),
                    "type": entity.get("label", ""),
                    "confidence": entity.get("score", 0.0),
                    "position": get_word_positions(text, entity.get("text", ""), entity.get("start", None)),
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
