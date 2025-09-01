import re

DEMONYM_TO_COUNTRY_EN = {
    "russian": "russia",
    "chinese": "china",
    "french": "france",
    "spanish": "spain",
    "german": "germany",
    "italian": "italy",
    "british": "united kingdom",
    "english": "england",
    "american": "united states",
    "dutch": "netherlands",
    "swiss": "switzerland",
    "turkish": "turkey",
    "polish": "poland",
    "swedish": "sweden",
    "norwegian": "norway",
    "danish": "denmark",
    "finnish": "finland",
    "greek": "greece",
    "portuguese": "portugal",
    "austrian": "austria",
    "ukrainian": "ukraine",
    "belarusian": "belarus",
    "czech": "czechia",
    "slovak": "slovakia",
    "hungarian": "hungary",
    "romanian": "romania",
    "bulgarian": "bulgaria",
    "serbian": "serbia",
    "croatian": "croatia",
    "bosnian": "bosnia and herzegovina",
    "slovenian": "slovenia",
    "albanian": "albania",
    "macedonian": "north macedonia",
    "irish": "ireland",
    "scottish": "scotland",
    "welsh": "wales",
    "estonian": "estonia",
    "latvian": "latvia",
    "lithuanian": "lithuania",
}

DEMONYM_TO_COUNTRY_DE = {
    "russisch": "russland",
    "chinesisch": "china",
    "französisch": "frankreich",
    "spanisch": "spanien",
    "deutsch": "deutschland",
    "italienisch": "italien",
    "britisch": "vereinigtes königreich",
    "englisch": "england",
    "amerikanisch": "vereinigte staaten",
    "niederländisch": "niederlande",
    "schweizerisch": "schweiz",
    "türkisch": "türkei",
    "polnisch": "polen",
    "schwedisch": "schweden",
    "norwegisch": "norwegen",
    "dänisch": "dänemark",
    "finnisch": "finnland",
    "griechisch": "griechenland",
    "portugiesisch": "portugal",
    "österreichisch": "österreich",
    "ukrainisch": "ukraine",
    "belarussisch": "belarus",
    "tschechisch": "tschechien",
    "slowakisch": "slowakei",
    "ungarisch": "ungarn",
    "rumänisch": "rumänien",
    "bulgarisch": "bulgarien",
    "serbisch": "serbien",
    "kroatisch": "kroatien",
    "bosnisch": "bosnien und herzegowina",
    "slowenisch": "slowenien",
    "albanisch": "albanien",
    "makedonisch": "nordmazedonien",
    "irisch": "irland",
    "schottisch": "schottland",
    "walisisch": "wales",
    "estnisch": "estland",
    "lettisch": "lettland",
    "litauisch": "litauen",
}

IRREGULAR_PLURALS = {
    "people": "person",
    "men": "man",
    "women": "woman",
    "children": "child",
    "mice": "mouse",
    "geese": "goose",
    "indices": "index",
    "matrices": "matrix",
    "data": "datum",
    "media": "medium",
    "barracks": "barracks",
    "police": "police",
    "behörden": "behörde",
    "unternehmen": "unternehmen",
    "universitäten": "universität",
    "parteien": "partei",
    "regierungen": "regierung",
    "städte": "stadt",
    "länder": "land",
    "regionen": "region",
    "zeiten": "zeit",
}


def normalize(s: str) -> str:
    # remove whitespaces and cast to lowercase
    # " Marty   Friedman"  -> "marty friedman"
    return re.sub(r"\s+", " ", s).strip().lower()


def tokenize_name(name: str) -> list[str]:
    # split on whitespace and simple punctuation
    # "ralf schumacher" -> ["ralf", "schumacher"]
    return [t for t in re.split(r"[^\wÀ-ÖØ-öø-ÿ]+", name) if t]


def singularize_word(word: str, lang: str = "en") -> str:
    # infer singular of a word based on the language
    # e.g. prices -> price, Katzen -> Katze

    if word in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[word]

    if lang == "de":
        if len(word) > 4:
            for suf in ("en", "n", "er", "s"):
                if word.endswith(suf):
                    return word[: -len(suf)]
    elif lang == "en":
        # English endings
        if re.search(r"[a-z]ies$", word):
            return re.sub(r"ies$", "y", word)
        if re.search(r"(xes|ses|zes|ches|shes)$", word):
            return re.sub(r"es$", "", word)
        if re.search(r"[a-z]s$", word) and not re.search(r"(ss|us|is)$", word):
            return word[:-1]
    return word


def map_demonym_to_country(entity: str) -> str | None:
    # nationality adjectives to country names
    # e.g. russian -> Russia

    if entity in DEMONYM_TO_COUNTRY_EN:
        return DEMONYM_TO_COUNTRY_EN[entity]

    GER_ENDINGS = ("e", "er", "en", "em", "es", "ische", "ischen", "ischem", "ischer", "isches")
    base = re.sub(rf"({'|'.join(map(re.escape, GER_ENDINGS))})$", "", entity)
    de_key = entity if entity in DEMONYM_TO_COUNTRY_DE else base
    if de_key in DEMONYM_TO_COUNTRY_DE:
        return DEMONYM_TO_COUNTRY_DE[de_key]

    return None


def deduplication(entities: list[dict]) -> list[dict]:
    # remove duplicates
    best = {}
    for e in entities:
        key = normalize(e["text"])
        score = e.get("score", 0)
        # keep higher score, then longer text as tie-break
        if key not in best or (score, len(e["text"])) > (best[key].get("score", 0), len(best[key]["text"])):
            best[key] = e
    return list(best.values())


def drop_demonyms(entities: list[dict]) -> list[dict]:
    # if both a country name and its demonym exists (e.g. Russia and russian)
    # -> keep only country name
    texts = {normalize(e["text"]) for e in entities}
    to_drop_idcs = set()
    for e in entities:
        if e.get("type") != "Location":
            continue
        ent_txt = normalize(e["text"])
        country = map_demonym_to_country(ent_txt)
        if country and country in texts:
            to_drop_idcs.add(id(e))

    return [e for e in entities if id(e) not in to_drop_idcs]


def deduplicate_persons(entities: list[dict]) -> list[dict]:
    # if a person is mentioned twice in a text (e.g. Willem Defoe & Defoe)
    # -> drop the tag with only the last name

    persons = [e for e in entities if e["type"] == "Person"]
    singletons = []
    multi = []
    for p in persons:
        toks = tokenize_name(p["text"])
        (multi if len(toks) >= 2 else singletons).append((p, toks))

    to_drop_idcs = set()

    for single_ent, s_toks in singletons:
        s = s_toks[0] if s_toks else ""
        if not s:
            continue
        for multi_ent, m_toks in multi:
            if any(t == s for t in m_toks):
                to_drop_idcs.add(id(single_ent))
                break

    return [e for e in entities if id(e) not in to_drop_idcs]


def singularize(entities: list[dict], language: str = "en") -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for e in entities:
        text = e["text"]
        if toks := tokenize_name(text):
            head = toks[-1]
            stem = singularize_word(head, language)
            prefix = " ".join(toks[:-1]).lower()
            key = (prefix, stem)
        else:
            key = ("", singularize_word(text, language))
        groups.setdefault(key, []).append(e)

    # If within a group we have multiple variants (plural/singular), keep the one whose head matches the singular form
    # or, if multiple remain, prefer the shortest head (likely singular) then the longest full text (for case/extra info).
    cleaned = []
    for key, members in groups.items():
        if len(members) == 1:
            cleaned.append(members[0])
            continue

        # Rank: head matches exact singular > shorter head length > longer full text
        ranked = []
        for e in members:
            toks = tokenize_name(e["text"])
            head = toks[-1].lower() if toks else e["text"].lower()
            exact_singular_match = int(head == key[1])
            ranked.append((exact_singular_match, -len(head), len(e["text"]), e))
        ranked.sort(reverse=True)
        cleaned.append(ranked[0][3])

    cleaned_idx = {e["idx"] for e in cleaned}
    return [e for e in entities if e["idx"] in cleaned_idx]


def clean_entities(entities: list[dict], lang: str = "en") -> list[dict[str, str]]:
    # normalize whitespaces of entity texts
    cleaned_ents = [{**e, "text": normalize(e.get("text", "")), "idx": e.get("idx", id(e))} for e in entities if e.get("text", "").strip()]

    cleaned_ents = deduplication(cleaned_ents)
    cleaned_ents = drop_demonyms(cleaned_ents)
    cleaned_ents = deduplicate_persons(cleaned_ents)
    cleaned_ents = singularize(cleaned_ents, lang)

    # return the cleaned entities in their original form
    keep = {e["idx"] for e in cleaned_ents}
    return [e for e in entities if e.get("idx", id(e)) in keep]
