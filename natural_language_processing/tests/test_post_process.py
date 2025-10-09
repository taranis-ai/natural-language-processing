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


def test_dbpedia_lookup_filters_and_extracts_uris(requests_mock, dbpedia_url):
    docs = [
        {"resource": ["http://dbpedia.org/resource/Apple_II"], "score": [16163.686]},
        {"resource": ["http://dbpedia.org/resource/Apple_Inc."], "score": 14846.572},
        {"resource": ["http://dbpedia.org/resource/IOS"], "score": 12254.968},
        {"resource": ["http://dbpedia.org/resource/MacOS"], "score": 10904.498},
        {"resource": ["http://dbpedia.org/resource/Apple_Records"], "score": 10097.711},
    ]
    requests_mock.get(dbpedia_url, json={"docs": docs})
    res = pc.dbpedia_lookup("Apple", top_n=5, score_threshold=1000)
    assert res == {
        "http://dbpedia.org/resource/Apple_II",
        "http://dbpedia.org/resource/Apple_Inc.",
        "http://dbpedia.org/resource/IOS",
        "http://dbpedia.org/resource/MacOS",
        "http://dbpedia.org/resource/Apple_Records",
    }


def test_dbpedia_lookup_honors_top_n(requests_mock, dbpedia_url):
    docs = [
        {"resource": ["uri:1"], "score": 5000},
        {"resource": ["uri:2"], "score": 5000},
        {"resource": ["uri:3"], "score": 5000},  # ignored if top_n=2
    ]
    requests_mock.get(dbpedia_url, json={"docs": docs})

    res = pc.dbpedia_lookup("something", top_n=2, score_threshold=1000)
    assert res == {"uri:1", "uri:2"}


def test_dbpedia_lookup_http_error_returns_empty_set(requests_mock, dbpedia_url):
    requests_mock.get(dbpedia_url, status_code=503)

    res = pc.dbpedia_lookup("anything")
    assert res == set()


def test_dbpedia_lookup_timeout_returns_empty_set(monkeypatch, dbpedia_url):
    def raise_timeout(*args, **kwargs):
        raise TimeoutError("simulated timeout")

    monkeypatch.setattr(pc.requests, "get", raise_timeout)
    res = pc.dbpedia_lookup("anything")
    assert res == set()


def test_dbpedia_lookup_bad_json_returns_empty_set(requests_mock, dbpedia_url):
    requests_mock.get(dbpedia_url, text="not a json")
    res = pc.dbpedia_lookup("anything")
    assert res == set()


@pytest.mark.parametrize(
    "entities,expected",
    [
        (
            [{"text": "Commodore 64.", "label": "Product"}],
            [{"text": "Commodore 64", "label": "Product"}],
        ),
        (
            [{"text": "Hello!", "label": "MISC"}],
            [{"text": "Hello", "label": "MISC"}],
        ),
        (
            [{"text": "?Berlin?", "label": "Location"}],
            [{"text": "Berlin", "label": "Location"}],
        ),
        (
            [{"text": "!!!Wow!!!", "label": "MISC"}],
            [{"text": "Wow", "label": "MISC"}],
        ),
        (
            [{"text": "Jean-Luc", "label": "Person"}],
            [{"text": "Jean-Luc", "label": "Person"}],
        ),
        (
            [
                {"text": "Paris,", "label": "Location"},
                {"text": "London;", "label": "Location"},
            ],
            [
                {"text": "Paris", "label": "Location"},
                {"text": "London", "label": "Location"},
            ],
        ),
    ],
)
def test_remove_leading_trailing_punctuation(entities, expected):
    assert pc.remove_leading_trailing_punctuation(entities) == expected


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
    "entities,text,expected",
    [
        (
            [
                {"text": "prices", "label": "MISC"},
                {"text": "price", "label": "MISC"},
            ],
            "We track the price daily.",
            {("price", "MISC")},
        ),
        (
            [
                {"text": "drones", "label": "Product"},
                {"text": "drone", "label": "Product"},
            ],
            "Multiple drones were sent out to detect unusual activity of the local wildlife.",
            {("drone", "Product")},
        ),
        (
            [{"text": "Apple stores", "label": "Location"}, {"text": "Apple store", "label": "Location"}],
            "Your local Apple stores will be restocked by the end of the week.",
            {("Apple store", "Location")},
        ),
        (
            [
                {"text": "Paläste", "label": "Location"},
            ],
            "Die Paläste wurden renoviert.",
            {("Paläste", "Location")},
        ),
        (
            [
                {"text": "Katzen", "label": "MISC"},
                {"text": "Katze", "label": "MISC"},
            ],
            "Mehrere Katzen kamen zusammen um sich über die Aufnahme einer neuen Katze zu beraten.",
            {("Katze", "MISC")},
        ),
        (
            [
                {"text": "Marshmallow", "label": "Product"},
                {"text": "Marshmallow", "label": "Organization"},
            ],
            "Marshmallows by the company aptly named Marshmallow, are really good.",
            {("Marshmallow", "Product"), ("Marshmallow", "Organization")},
        ),
        (
            [
                {"text": "Nachbarn", "label": "Person"},
                {"text": "Nachbar", "label": "Person"},
            ],
            "Die Nachbarn störten schon wieder einmal die Nachtruhe",
            {("Nachbar", "Person")},
        ),
        (
            [
                {"text": "Technischen Universitäten", "label": "Organization"},
                {"text": "Technische Universität", "label": "Organization"},
            ],
            "Die Technischen Universitäten sind von zweifelhaftem Ruf. Überhaupt die Technische Universität Wels.",
            {("Technische Universität", "Organization")},
        ),
        (
            [{"text": "geese", "label": "Animal"}],
            "Many geese form a gaggle.",
            {("geese", "Animal")},
        ),
        (
            [{"text": "Handy", "label": "Product"}, {"text": "Handy", "label": "Product"}],
            "Bundesweiter Warntag: Donnerstag bimmeln auch die Handys wieder. Am bundesweiten Warntag werden wieder Warnmeldungen per Handy, Radio und über weitere Kanäle verbreitet",
            {("Handy", "Product")},
        ),
        (
            [{"text": "Premium-Smartphones", "label": "Product"}, {"text": "Premium-Smartphone", "label": "Product"}],
            "Premium-Smartphones sind immer noch heiß begehrt. Jedoch erhält man für um die 600 euro mittlerweile auch ein Premium-Smartphone aus dem Vorjahr.",
            {("Premium-Smartphone", "Product")},
        ),
        (
            [{"text": "Fliegers", "label": "Product"}],
            "Vor Kurzem war das GPS des Fliegers von der Leyens betroffen.",
            {("Flieger", "Product")},
        ),
    ],
)
def test_deduplicate_by_lemma(entities, text, expected):
    result = pc.deduplicate_by_lemma(entities, text)
    got = {(e["text"], e["label"]) for e in result}
    assert got == expected


@pytest.mark.parametrize(
    "entities, uri_map, expected",
    [
        # US & USA -> keep only USA
        (
            [
                {"text": "US", "label": "Location"},
                {"text": "USA", "label": "Location"},
            ],
            {"US": {"uri:United States", "uri:US Air Force"}, "USA": {"uri:United States", "uri:US Army"}},
            [{"text": "USA", "label": "Location"}],
        ),
        # UK, United Kingdom & Great Britain
        (
            [
                {"text": "UK", "label": "Location"},
                {"text": "United Kingdom", "label": "Location"},
                {"text": "Great Britain", "label": "Location"},
            ],
            {
                "UK": {"uri:uk"},
                "United Kingdom": {"uri:uk"},
                "Great Britain": {"uri:uk"},
            },
            [
                {"text": "United Kingdom", "label": "Location"},
            ],
        ),
        # MoI, Ministry of the Interior -> keep Ministry ...
        (
            [
                {"text": "MoI", "label": "Organization"},
                {"text": "Ministry of the Interior", "label": "Organization"},
            ],
            {
                "MoI": {"uri:Ministry of Interior"},
                "Ministry of the Interior": {"uri:Ministry of Interior"},
            },
            [{"text": "Ministry of the Interior", "label": "Organization"}],
        ),
        # no lookup hits -> keep everything as-is ---
        (
            [
                {"text": "Xanadu", "label": "Location"},
                {"text": "Neverland", "label": "Location"},
            ],
            {},
            [
                {"text": "Xanadu", "label": "Location"},
                {"text": "Neverland", "label": "Location"},
            ],
        ),
        # --- tie length for same URI -> keep the first occurrence ---
        (
            [
                {"text": "GB", "label": "Location"},
                {"text": "UK", "label": "Location"},
            ],
            {
                "GB": {"uri:uk"},
                "UK": {"uri:uk"},
            },
            [
                {"text": "GB", "label": "Location"},
            ],
        ),
    ],
)
def test_deduplicate_by_linking(monkeypatch, entities, uri_map, expected):
    def fake_lookup(_):
        # Simulate dbpedia_lookup using normalized text keys.
        return uri_map

    monkeypatch.setattr(pc, "dbpedia_lookup", fake_lookup)

    res = pc.deduplicate_by_linking(entities)
    assert res == expected


def test_clean_entities_en(entities_en):
    entities, text = entities_en
    cleaned = pc.clean_entities(entities, text)

    assert any(e["text"] == "Russia" for e in cleaned)
    assert all(e["text"] != "russian" for e in cleaned)

    assert any(e["text"] == "Willem Defoe" for e in cleaned)
    assert all(e["text"] != "Defoe" for e in cleaned)

    assert any(e["text"] == "price" for e in cleaned)
    assert all(e["text"] != "prices" for e in cleaned)


def test_clean_entities_de(entities_de):
    entities, text = entities_de
    cleaned = pc.clean_entities(entities, text)

    assert any(e["text"] == "Spanien" for e in cleaned)
    assert all(e["text"] != "Spanier" for e in cleaned)

    assert any(e["text"] == "Russland" for e in cleaned)
    assert all(e["text"] != "russischen" for e in cleaned)

    assert any(e["text"] == "Katze" for e in cleaned)
    assert all(e["text"] != "Katzen" for e in cleaned)

    assert any(e["text"] == "William S. Burroughs" for e in cleaned)
    assert all(e["text"] != "Burroughs" for e in cleaned)
