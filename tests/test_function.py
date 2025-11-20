import pytest
from jsonschema import validate


def assert_entities(result: dict[str, str], expected: dict[str, set]) -> None:
    """Assert that all expected entities are present with correct labels.
    Order-independent and tolerant to extra entities in 'result'."""
    missing = set(expected) - set(result)
    assert not missing, f"Missing entities: {missing}"

    mislabelled = []
    mislabelled.extend(entity for entity, entity_type_set in expected.items() if result.get(entity) not in entity_type_set)
    assert not mislabelled, f"Mislabelled entities: {mislabelled}"


@pytest.mark.parametrize(
    "model_fixture,text_fixture,expected,cybersecurity",
    [
        (
            "roberta",
            "example_text",
            {"ACME Corporation": "Organization", "Acme City": "Location", "Australia": "Location", "Dynamite": "MISC"},
            False,
        ),
        ("roberta_german", "example_text_de", {"ACME Corporation": "Organization", "Acme City": "Location", "Australien": "Location"}, False),
        (
            "gliner",
            "example_text",
            {"ACME Corporation": "Organization", "Acme City": "Location", "Australia": "Location", "Dynamite": "Product"},
            False,
        ),
        ("gliner", "example_cybersec_text", {"Emotet": "Malware", "Microsoft 365": "Product"}, True),
    ],
)
def test_ner_models(
    request: pytest.FixtureRequest,
    model_fixture: str,
    text_fixture: str,
    expected: dict,
    cybersecurity: bool,
    extended_output_schema: dict,
):
    model = request.getfixturevalue(model_fixture)
    text = request.getfixturevalue(text_fixture)

    if cybersecurity:
        result = model.predict(text, extended_output=False, cybersecurity=cybersecurity)
    else:
        result = model.predict(text, extended_output=False)
    assert isinstance(result, dict)
    assert_entities(result, expected)

    if cybersecurity:
        extended = model.predict(text, extended_output=True, cybersecurity=cybersecurity)
    else:
        extended = model.predict(text, extended_output=True)

    validate(instance=extended, schema=extended_output_schema)


@pytest.mark.parametrize(
    "model_fixture",
    ["roberta", "roberta_german", "gliner"],
)
def test_ner_on_articles(request: pytest.FixtureRequest, model_fixture: str, article: tuple[str, dict]):
    content, expected = article
    model = request.getfixturevalue(model_fixture)
    result = model.predict(content)
    assert_entities(result, expected)
