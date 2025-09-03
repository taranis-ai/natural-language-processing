from flair.models import SequenceTagger
from flair.data import Sentence

from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor


class FlairNER(Predictor):
    model_name = "flair/ner-english"

    def __init__(self):
        self.model = SequenceTagger.load(self.model_name)

    def predict(self, text: str, extended_output: bool = False, is_cybersecurity: bool = False) -> dict[str, str] | list[dict]:
        sentence = Sentence(text)
        self.model.predict(sentence)

        if extended_output:
            out_list = []
            out_list.extend(
                {"value": span.text, "type": span.tag, "probability": span.score, "position": f"{span.start_position}-{span.end_position}"}
                for span in sentence.get_spans("ner")
                if span.score >= Config.confidence_threshold
            )
            return out_list
        return {
            ner_result.data_point.text: ner_result.value
            for ner_result in sentence.get_labels()
            if ner_result.score >= Config.confidence_threshold
        }
