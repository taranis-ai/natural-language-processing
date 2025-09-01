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
        ("O’Connor", ["O", "Connor"]),
        ("Müller-Lüdenscheidt", ["Müller", "Lüdenscheidt"]),
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
    "inp,expected",
    [
        ("russian", "russia"),
        ("german", "germany"),
        ("lithuanian", "lithuania"),
        ("amerikanischen", "vereinigte staaten"),  # stripped to base "amerikanisch"
        ("russischen", "russland"),
        ("unknown", None),
    ],
)
def test_map_demonym_to_country(inp, expected):
    assert pc.map_demonym_to_country(pc.normalize(inp)) == expected
