from flair.models import SequenceTagger
from flair.data import Sentence

from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor


class FlairNER(Predictor):
    model_name = "flair/ner-english"

    def __init__(self):
        self.model = SequenceTagger.load(self.model_name)

    def predict(self, text: str) -> dict[str, str]:
        sentence = Sentence(text)
        self.model.predict(sentence)

        return {ent.data_point.text: ent.value for ent in sentence.get_labels() if ent.score >= Config.confidence_threshold}
