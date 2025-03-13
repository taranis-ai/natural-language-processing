from natural_language_processing.roberta_ner import RobertaNER
from natural_language_processing.flair_ner import FlairNER
from natural_language_processing.mpnet_ner import MPNETNer


def test_exapmle_ner_flair(example_text: str, flair_model: FlairNER):
    result = flair_model.predict(example_text)
    expected = {"Australia": "LOC", "Wile E. Coyote": "PER"}
    missed_entities = {entity for entity in expected if entity not in result}
    assert not missed_entities, f"Not all expected entities were identified: {missed_entities}"
    mislabelled_entities = {entity for entity, label in expected.items() if result[entity] != label}
    assert not mislabelled_entities, f"Not all expected entities were labelled correctly: {mislabelled_entities}"


def test_example_ner_roberta(example_text: str, roberta_model: RobertaNER):
    result = roberta_model.predict(example_text)
    expected = {"ACME Corporation": "ORG", "Acme City": "LOC", "Australia": "LOC", "Dynamite": "MISC"}
    missed_entities = {entity for entity in expected if entity not in result}
    assert not missed_entities, f"Not all expected entities were identified: {missed_entities}"
    mislabelled_entities = {entity for entity, label in expected.items() if result[entity] != label}
    assert not mislabelled_entities, f"Not all expected entities were labelled correctly: {mislabelled_entities}"


def test_example_ner_mpnet(example_cybersec_text: str, mpnet_model: MPNETNer):
    result = mpnet_model.predict(example_cybersec_text)
    expected = {"Emotet": "MALWARE", "Microsoft": "ORG"}

    missed_entities = {entity for entity in expected if entity not in result}
    assert not missed_entities, f"Not all expected entities were identified: {missed_entities}"
    mislabelled_entities = {entity for entity, label in expected.items() if result[entity] != label}
    assert not mislabelled_entities, f"Not all expected entities were labelled correctly: {mislabelled_entities}"


def test_ner_flair(article: tuple[str, list], flair_model: FlairNER):
    content, expected = article
    result = flair_model.predict(content)
    missed_entities = {entity for entity in expected if entity not in result}
    assert not missed_entities, f"Not all expected entities were identified: {missed_entities}"
    mislabelled_entities = {entity for entity, label in expected.items() if result[entity] != label}
    assert not mislabelled_entities, f"Not all expected entities were labelled correctly: {mislabelled_entities}"


def test_ner_roberta(article: tuple[str, list], roberta_model: RobertaNER):
    content, expected = article
    result = roberta_model.predict(content)
    missed_entities = {entity for entity in expected if entity not in result}
    assert not missed_entities, f"Not all expected entities were identified: {missed_entities}"
    mislabelled_entities = {entity for entity, label in expected.items() if result[entity] != label}
    assert not mislabelled_entities, f"Not all expected entities were labelled correctly: {mislabelled_entities}"
