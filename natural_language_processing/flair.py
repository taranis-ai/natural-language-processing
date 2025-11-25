from flair.models import SequenceTagger
from flair.data import Sentence

from natural_language_processing.config import Config
from natural_language_processing.post_process import map_entity_types, is_entity_allowed


class Flair:
    model_name = "flair/ner-english"

    def __init__(self):
        self.model = SequenceTagger.load(self.model_name)

    def predict(self, text: str, extended_output: bool = False) -> dict[str, str] | list[dict]:
        sentence = Sentence(text)
        self.model.predict(sentence)

        if extended_output:
            out_list = []
            out_list.extend(
                {
                    "value": span.text,
                    "type": map_entity_types(span.tag),
                    "probability": span.score,
                    "position": f"{span.start_position}-{span.end_position}",
                }
                for span in sentence.get_spans("ner")
                if span.score >= Config.CONFIDENCE_THRESHOLD and is_entity_allowed(map_entity_types(span.tag), Config.ENTITIES)
            )
            return out_list
        return {
            ner_result.data_point.text: map_entity_types(ner_result.value)
            for ner_result in sentence.get_labels()
            if ner_result.score >= Config.CONFIDENCE_THRESHOLD and is_entity_allowed(map_entity_types(ner_result.value), Config.ENTITIES)
        }
