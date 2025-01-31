from natural_language_processing.config import Config


class NLPProcessor:
    """
    Wrapper class for Models to allow for conditional imports based on the Config.MODEL setting
    """

    def __init__(self):
        if Config.MODEL == "flair":
            from natural_language_processing.flair_ner import FlairNER

            self.model = FlairNER()
        elif Config.MODEL == "roberta":
            from natural_language_processing.roberta_ner import RobertaNER

            self.model = RobertaNER()
        elif Config.MODEL == "roberta_german":
            from natural_language_processing.roberta_ner_german import RobertaGermanNER

            self.model = RobertaGermanNER()
        else:
            raise ValueError(f"Unsupported NER model: {Config.MODEL}")

    def predict(self, text: str) -> dict[str, str]:
        return self.model.predict(text)

    def modelinfo(self) -> dict[str, str]:
        return self.model.modelinfo
