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
    "word,expected",
    [
        ("companies", "company"),
        ("batteries", "battery"),
        ("buses", "bus"),
        ("analyses", "analysis"),
        ("police", "police"),
        ("data", "datum"),
        ("status", "status"),
    ],
)
def test_singularize_word_en(word, expected):
    assert pc.singularize_word(word, "en") == expected


@pytest.mark.parametrize(
    "word,expected",
    [("Schafe", "Schaf"), ("Veranstaltungen", "Veranstaltung"), ("Syteme", "System")],
)
def test_singularize_word_de(word, expected):
    assert pc.singularize_word(word, "de") == expected


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
