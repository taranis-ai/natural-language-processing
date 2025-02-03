from natural_language_processing.roberta_ner import RobertaNER
from natural_language_processing.flair_ner import FlairNER


def test_analyze_ner_flair(example_text: str, flair_analyzer: FlairNER):
    result = flair_analyzer.predict(example_text)
    expected = {"Australia": "LOC", "Wile E. Coyote": "PER"}
    assert expected.items() <= result.items()


def test_analyze_ner_roberta(example_text: str, roberta_analyzer: RobertaNER):
    result = roberta_analyzer.predict(example_text)
    expected = {"ACME Corporation": "ORG", "Acme City": "LOC", "Australia": "LOC", "Dynamite": "MISC"}
    assert expected.items() <= result.items()
