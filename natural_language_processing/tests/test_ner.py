from natural_language_processing.roberta_ner import RobertaNER
from natural_language_processing.flair_ner import FlairNER


def test_exapmle_ner_flair(example_text: str, flair_model: FlairNER):
    result = flair_model.predict(example_text)
    expected = {"Australia": "LOC", "Wile E. Coyote": "PER"}
    assert all(word in result.items() for word in expected.items()), f"Not all expected keywords were found in the summary: {result}"


def test_example_ner_roberta(example_text: str, roberta_model: RobertaNER):
    result = roberta_model.predict(example_text)
    expected = {"ACME Corporation": "ORG", "Acme City": "LOC", "Australia": "LOC", "Dynamite": "MISC"}
    assert all(word in result.items() for word in expected.items()), f"Not all expected keywords were found in the summary: {result}"


def test_ner_flair(article: tuple[str, list], flair_model: FlairNER):
    content, expected = article
    result = flair_model.predict(content)
    assert all(word in result.keys() for word in expected), f"Not all expected keywords were found in the summary: {result.keys()}"


def test_ner_roberta(article: tuple[str, list], roberta_model: RobertaNER):
    content, expected = article
    result = roberta_model.predict(content)
    assert all(word in result.keys() for word in expected), f"Not all expected keywords were found in the summary: {result.keys()}"
