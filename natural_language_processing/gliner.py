from gliner import GLiNER
from natural_language_processing.config import Config
from natural_language_processing.post_process import clean_entities


def map_cybersec_entities(cybersec_entities: list[dict[str, str]]) -> list[dict[str, str]]:
    mapped_entities = []
    for entity in cybersec_entities:
        if entity.get("label", "") == "CON":
            mapped_entities.append({**entity, "label": "Concept"})
        else:
            mapped_entities.append({**entity, "label": entity.get("label", "").capitalize()})
    return mapped_entities


def merge_with_cybersec_priority(general_entities: list[dict], cybersec_entities: list[dict]) -> list[dict]:
    def make_key(entity):
        return (
            (entity["start"], entity["end"])
            if entity.get("start") is not None and entity.get("end") is not None
            else (entity.get("text", "") or "").strip().lower()
        )

    merged = {make_key(e): e for e in general_entities}
    merged.update({make_key(e): e for e in cybersec_entities})
    return list(merged.values())


def transform_result(entities: list[dict]) -> list[dict]:
    if not entities:
        return []
    return [{**e, "type": e.get("label"), "idx": i} for i, e in enumerate(entities)]


class Gliner:
    def __init__(self):
        self.general_model = GLiNER.from_pretrained("llinauer/gliner_de_en_news")
        self.general_labels = ["Person", "Location", "Organization", "Product", "Address"]
        self.cybersec_model = GLiNER.from_pretrained("selfconstruct3d/AITSecNER", load_tokenizer=True)
        self.cybersec_labels = ["CLICommand/CodeSnippet", "CON", "GROUP", "MALWARE", "SECTOR", "TACTIC", "TECHNIQUE", "TOOL"]

    def predict(self, text: str, extended_output: bool = False, is_cybersecurity: bool = False) -> dict[str, str] | list[dict]:
        general_entities = self.general_model.predict_entities(text, self.general_labels, threshold=Config.CONFIDENCE_THRESHOLD)
        if is_cybersecurity:
            cybersec_entities = self.cybersec_model.predict_entities(text, self.cybersec_labels, threshold=Config.CONFIDENCE_THRESHOLD)
            cybersec_entities = map_cybersec_entities(cybersec_entities)
        else:
            cybersec_entities = []

        entities = merge_with_cybersec_priority(general_entities, cybersec_entities)

        if not entities:
            return [] if extended_output else {}

        entities = clean_entities(transform_result(entities), text)

        if extended_output:
            out_list = []
            out_list.extend(
                {
                    "value": entity.get("text", ""),
                    "type": entity.get("type", ""),
                    "probability": entity.get("score", 0.0),
                    "position": f"{entity.get('start', '')}-{entity.get('end', '')}",
                }
                for entity in entities
                if isinstance(entity, dict) and entity.get("score", 0) > Config.CONFIDENCE_THRESHOLD and entity.get("text") is not None
            )
            return out_list

        return {
            entity["text"]: entity.get("label", "")
            for entity in entities
            if isinstance(entity, dict) and entity.get("score", 0) > Config.CONFIDENCE_THRESHOLD and entity.get("text") is not None
        }
