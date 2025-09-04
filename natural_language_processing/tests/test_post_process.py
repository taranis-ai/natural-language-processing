import pytest
import natural_language_processing.post_process as pc


@pytest.mark.parametrize(
    "s,expected",
    [
        (" Marty   Friedman ", "marty friedman"),
        ("A\tB\nC", "a b c"),
        ("  ÄÖ Ü  ", "äö ü"),
        ("", ""),
    ],
)
def test_normalize(s, expected):
    assert pc.normalize(s) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("ralf schumacher", ["ralf", "schumacher"]),
        ("Jean-Luc Picard", ["Jean", "Luc", "Picard"]),
        ("Sean O’Connor", ["Sean", "O", "Connor"]),
        ("Hans Müller-Lüdenscheidt", ["Hans", "Müller", "Lüdenscheidt"]),
        ("APT29", ["APT29"]),
        ("", []),
    ],
)
def test_tokenize_name(name, expected):
    assert pc.tokenize_name(name) == expected


@pytest.mark.parametrize(
    "word,lang,expected",
    [
        ("dogs", "en", "dog"),
        ("cars", "en", "car"),
        ("houses", "en", "house"),
        ("men", "en", "man"),
        ("women", "en", "woman"),
        ("children", "en", "child"),
        ("mice", "en", "mouse"),
        ("wolves", "en", "wolf"),
        ("indices", "en", "index"),
        ("matrices", "en", "matrix"),
        ("Katzen", "de", "Katze"),
        ("Häuser", "de", "Haus"),
        ("Bücher", "de", "Buch"),
        ("Männer", "de", "Mann"),
        ("Frauen", "de", "Frau"),
        ("Städte", "de", "Stadt"),
    ],
)
def test_singularize_word(word, lang, expected):
    assert pc.singularize_word(word, lang) == expected


@pytest.mark.parametrize(
    "word,expected",
    [
        ("chinesische", "chinesisch"),
        ("Chinesischen", "Chinesisch"),
        ("russische", "russisch"),
        ("Russischem", "Russisch"),
        ("französisches", "französisch"),
        ("deutsche", "deutsch"),
        ("deutschen", "deutsch"),
        ("deutscher", "deutsch"),
        ("deutschem", "deutsch"),
        ("österreicher", "österreich"),
        ("spanisch", "spanisch"),
        ("polnisch", "polnisch"),
    ],
)
def test_normalize_de_demonym_form(word, expected):
    assert pc.normalize_de_demonym_form(word) == expected


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("russian", "russia"),
        ("german", "germany"),
        ("lithuanian", "lithuania"),
        ("amerikanischen", "vereinigte staaten"),
        ("russischen", "russland"),
        ("unknown", None),
        ("deutsche", "deutschland"),
        ("schweizerisch", "schweiz"),
        ("finnisch", "finnland"),
        ("chinese", "china"),
        ("spanier", "spanien"),
        ("spanierinnen", "spanien"),
    ],
)
def test_map_demonym_to_country(inp, expected):
    assert pc.map_demonym_to_country(inp) == expected


def test_deduplication():
    raw_entities = [
        ("Drone", "Product"),
        ("drone", "Product"),
        ("Karl Landsteiner", "Person"),
        ("karl Landsteiner", "Person"),
        ("Apple", "Organization"),
        ("apple", "Product"),
        ("united Nations", "Organization"),
        ("United Nations", "Organization"),
    ]
    raw_entities = [{"text": e[0], "label": e[1]} for e in raw_entities]
    processed_entities = pc.deduplication(raw_entities)
    assert processed_entities == [
        {"text": "Drone", "label": "Product"},
        {"text": "Karl Landsteiner", "label": "Person"},
        {"text": "Apple", "label": "Organization"},
        {"text": "apple", "label": "Product"},
        {"text": "United Nations", "label": "Organization"},
    ]


@pytest.mark.parametrize(
    "entities,expected",
    [
        (
            [{"text": "Russia", "label": "Location"}, {"text": "russian", "label": "Location"}],
            [{"text": "Russia", "label": "Location"}],
        ),
        (
            [{"text": "russian", "label": "Location"}, {"text": "Berlin", "label": "Location"}],
            [{"text": "russian", "label": "Location"}, {"text": "Berlin", "label": "Location"}],
        ),
        (
            [{"text": "RUSSIA", "label": "Location"}, {"text": "Russian", "label": "Location"}],
            [{"text": "RUSSIA", "label": "Location"}],
        ),
        (
            [{"text": "Russia", "label": "Location"}, {"text": "russian", "label": "Organization"}],
            [{"text": "Russia", "label": "Location"}, {"text": "russian", "label": "Organization"}],
        ),
    ],
)
def test_drop_demonyms(entities, expected):
    assert pc.drop_demonyms(entities) == expected


@pytest.mark.parametrize(
    "entities,expected",
    [
        (
            [
                {"text": "Willem Defoe", "label": "Person"},
                {"text": "Defoe", "label": "Person"},
                {"text": "Random Corp", "label": "Organization"},
            ],
            [
                {"text": "Willem Defoe", "label": "Person"},
                {"text": "Random Corp", "label": "Organization"},
            ],
        ),
        (
            [
                {"text": "Defoe", "label": "Person"},
                {"text": "Random Corp", "label": "Organization"},
            ],
            [
                {"text": "Defoe", "label": "Person"},
                {"text": "Random Corp", "label": "Organization"},
            ],
        ),
        (
            [
                {"text": "WILLEM DEFOE", "label": "Person"},
                {"text": "defoe", "label": "Person"},
            ],
            [
                {"text": "WILLEM DEFOE", "label": "Person"},
            ],
        ),
        (
            [
                {"text": "John Ronald Reuel Tolkien", "label": "Person"},
                {"text": "Tolkien", "label": "Person"},
                {"text": "John Ronald", "label": "Person"},
            ],
            [
                {"text": "John Ronald Reuel Tolkien", "label": "Person"},
                {"text": "John Ronald", "label": "Person"},
            ],
        ),
        (
            [
                {"text": "John Smith", "label": "Person"},
                {"text": "Anna Smith", "label": "Person"},
                {"text": "Smith", "label": "Person"},
            ],
            [
                {"text": "John Smith", "label": "Person"},
                {"text": "Anna Smith", "label": "Person"},
            ],
        ),
        (
            [
                {"text": "Berlin", "label": "Location"},
                {"text": "Doe", "label": "Organization"},
                {"text": "John Doe", "label": "Person"},
                {"text": "Doe", "label": "Person"},
            ],
            [
                {"text": "Berlin", "label": "Location"},
                {"text": "Doe", "label": "Organization"},
                {"text": "John Doe", "label": "Person"},
            ],
        ),
    ],
)
def test_deduplicate_persons(entities, expected):
    assert pc.deduplicate_persons(entities) == expected


@pytest.mark.parametrize(
    "language,entities,expected",
    [
        (
            "en",
            [
                {"idx": 1, "text": "prices", "label": "MISC"},
                {"idx": 2, "text": "price", "label": "MISC"},
            ],
            [
                {"idx": 2, "text": "price", "label": "MISC"},
            ],
        ),
        (
            "en",
            [
                {"idx": 1, "text": "drones", "label": "Product"},
                {"idx": 2, "text": "drone", "label": "Product"},
            ],
            [
                {"idx": 2, "text": "drone", "label": "Product"},
            ],
        ),
        (
            "en",
            [
                {"idx": 1, "text": "Apple Stores", "label": "Location"},
                {"idx": 2, "text": "Apple Store", "label": "Location"},
            ],
            [
                {"idx": 2, "text": "Apple Store", "label": "Location"},
            ],
        ),
        (
            "en",
            [
                {"idx": 1, "text": "busses", "label": "Product"},
                {"idx": 2, "text": "smartphones", "label": "Product"},
            ],
            [
                {"idx": 1, "text": "busses", "label": "Product"},
                {"idx": 2, "text": "smartphones", "label": "Product"},
            ],
        ),
        (
            "de",
            [
                {"idx": 1, "text": "Schulen", "label": "Location"},
                {"idx": 2, "text": "Schule", "label": "Location"},
            ],
            [
                {"idx": 2, "text": "Schule", "label": "Location"},
            ],
        ),
        (
            "de",
            [
                {"idx": 1, "text": "Technische Universitäten", "label": "Organization"},
                {"idx": 2, "text": "Technische Universität", "label": "Organization"},
            ],
            [
                {"idx": 2, "text": "Technische Universität", "label": "Organization"},
            ],
        ),
        (
            "en",
            [
                {"idx": 1, "text": "Marshmallow", "label": "Product"},
                {"idx": 2, "text": "Marshmallow", "label": "Organization"},
            ],
            [
                {"idx": 1, "text": "Marshmallow", "label": "Product"},
                {"idx": 2, "text": "Marshmallow", "label": "Organization"},
            ],
        ),
    ],
)
def test_singularize(language, entities, expected):
    assert pc.singularize(entities, language) == expected


def test_clean_entities_en(entities_en):
    cleaned = pc.clean_entities(entities_en, lang="en")

    assert any(e["text"] == "Russia" for e in cleaned)
    assert all(e["text"] != "russian" for e in cleaned)

    assert any(e["text"] == "Willem Defoe" for e in cleaned)
    assert all(e["text"] != "Defoe" for e in cleaned)

    assert any(e["text"] == "price" for e in cleaned)
    assert all(e["text"] != "prices" for e in cleaned)


def test_clean_entities_de(entities_de):
    cleaned = pc.clean_entities(entities_de, lang="de")

    assert any(e["text"] == "Spanien" for e in cleaned)
    assert all(e["text"] != "Spanier" for e in cleaned)

    assert any(e["text"] == "Russland" for e in cleaned)
    assert all(e["text"] != "russischen" for e in cleaned)

    assert any(e["text"] == "Katze" for e in cleaned)
    assert all(e["text"] != "Katzen" for e in cleaned)

    assert any(e["text"] == "William S. Burroughs" for e in cleaned)
    assert all(e["text"] != "Burroughs" for e in cleaned)
