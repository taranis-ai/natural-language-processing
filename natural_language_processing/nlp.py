import json
from flair.models import SequenceTagger
from flair.data import Sentence

class NLPProcessor:
    def __init__(self):
        # Load only the English model during initialization
        self.model = SequenceTagger.load("flair/ner-english")

        # Uncomment and modify this when adding support for multiple languages.
        """
        with open(config_path, 'r') as f:
            self.model_mapping = json.load(f)
            
        self.models = {
            lang: SequenceTagger.load(model_name)
            for lang, model_name in self.model_mapping.items()
        }
        """


    def predict(self, text: str, language: str = "en"):
        # Uncomment this when adding multiple languages support.
        """
        if language not in self.models:
            raise ValueError(f"Language {language} is not supported.")
        
        # Select the model for the given language, defaulting to English if not found
        tagger = self.models.get(language, self.models['en'])
        """

        # Default behavior: use the pre-loaded English model
        tagger = self.model

        sentence = Sentence(text)
        tagger.predict(sentence)

        keywords = {ent.data_point.text: ent.value for ent in sentence.get_labels()}
        return keywords