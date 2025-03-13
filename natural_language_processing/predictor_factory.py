from natural_language_processing.config import Config
from natural_language_processing.predictor import Predictor


class PredictorFactory:
    """
    Factory class that dynamically instantiates and returns the correct Predictor
    based on the configuration. This approach ensures that only the configured model
    is loaded at startup.
    """

    def __new__(cls, *args, **kwargs) -> Predictor:
        if Config.MODEL == "flair":
            from natural_language_processing.flair_ner import FlairNER

            return FlairNER(*args, **kwargs)
        elif Config.MODEL == "roberta":
            from natural_language_processing.roberta_ner import RobertaNER

            return RobertaNER(*args, **kwargs)
        elif Config.MODEL == "roberta_german":
            from natural_language_processing.roberta_ner_german import RobertaGermanNER

            return RobertaGermanNER(*args, **kwargs)
        elif Config.MODEL == "mpnet":
            from natural_language_processing.mpnet_ner import MPNETNer

            return MPNETNer(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported NER model: {Config.MODEL}")
