import pytest
from jsonschema import validate


def assert_entities(result: dict[str, str], expected: dict[str, str]) -> None:
    """Assert that all expected entities are present with correct labels.
    Order-independent and tolerant to extra entities in 'result'."""
    missing = set(expected) - set(result)
    assert not missing, f"Missing entities: {missing}"

    mislabelled = {ent: (expected[ent], result[ent]) for ent in expected if result.get(ent) != expected[ent]}
    assert not mislabelled, f"Mislabelled entities: {mislabelled}"


@pytest.mark.parametrize(
    "model_fixture,text_fixture,expected,is_cybersecurity",
    [
        ("flair_model", "example_text", {"Australia": "LOC", "Wile E. Coyote": "PER"}, False),
        ("roberta_model", "example_text", {"ACME Corporation": "ORG", "Acme City": "LOC", "Australia": "LOC", "Dynamite": "MISC"}, False),
        (
            "gliner_model",
            "example_text",
            {"ACME Corporation": "Organization", "Acme City": "Location", "Australia": "Location", "Dynamite": "Product"},
            False,
        ),
        ("gliner_model", "example_cybersec_text", {"Emotet": "Malware", "Microsoft 365": "Product"}, True),
    ],
)
def test_ner_models(
    request: pytest.FixtureRequest,
    model_fixture: str,
    text_fixture: str,
    expected: dict,
    is_cybersecurity: bool,
    extended_output_schema: dict,
):
    model = request.getfixturevalue(model_fixture)
    text = request.getfixturevalue(text_fixture)

    result = model.predict(text, extended_output=False, is_cybersecurity=is_cybersecurity)
    assert isinstance(result, dict)
    assert_entities(result, expected)

    extended = model.predict(text, extended_output=True, is_cybersecurity=is_cybersecurity)
    validate(instance=extended, schema=extended_output_schema)


@pytest.mark.parametrize(
    "model_fixture",
    ["flair_model", "roberta_model"],
)
def test_ner_on_articles(request: pytest.FixtureRequest, model_fixture: str, article: tuple[str, dict]):
    content, expected = article
    model = request.getfixturevalue(model_fixture)
    result = model.predict(content)
    assert_entities(result, expected)
