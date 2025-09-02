import re
import inflect
import spacy

NLP_DE = spacy.load("de_core_news_sm", disable=["ner", "textcat"])
INFLECT = inflect.engine()

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
    "teeth": "tooth",
    "feet": "foot",
    "oxen": "ox",
    "lice": "louse",
    "dice": "die",
    "cacti": "cactus",
    "fungi": "fungus",
    "nuclei": "nucleus",
    "alumni": "alumnus",
    "syllabi": "syllabus",
    "indices": "index",
    "matrices": "matrix",
    "criteria": "criterion",
    "phenomena": "phenomenon",
    "appendices": "appendix",
    "theses": "thesis",
    "analyses": "analysis",
    "diagnoses": "diagnosis",
    "crises": "crisis",
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
    "männer": "mann",
    "frauen": "frau",
    "häuser": "haus",
    "bücher": "buch",
    "lieder": "lied",
    "bäume": "baum",
    "mäuse": "maus",
    "füße": "fuß",
    "kühe": "kuh",
    "eier": "ei",
    "wörter": "wort",
    "worte": "wort",
    "bilder": "bild",
    "töchter": "tochter",
    "brüder": "bruder",
    "väter": "vater",
    "mütter": "mutter",
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
        doc = NLP_DE(word)
        if not doc or len(doc) == 0:
            return word

        token = doc[0]
        lemma = token.lemma_ or word

        # Guard: keep capitalization of proper nouns if input looked like proper noun
        if word[:1].isupper() and lemma.islower():
            # German nouns are capitalized; keep original case for display
            return lemma.capitalize()
        return lemma
    elif lang == "en":
        singular = inflect.engine().singular_noun(word)
        return singular if singular else word
    return word


def normalize_de_demonym_form(word: str) -> str:
    # map demonyms ending with -isch to base form
    # e.g. schweizerischen -> schweizerisch, russischen -> russisch
    # map demonyms with common endings to base form
    # e.g. deutsche -> deutsch

    DE_ISCH_INFLECTED_RE = re.compile(r"^(.*?isch)(e|er|en|em|es)$", flags=re.IGNORECASE)
    if match := DE_ISCH_INFLECTED_RE.match(word):
        return match[1]

    DE_ADJ_ENDINGS = ("en", "er", "em", "es", "e")

    return next(
        (word[: -len(suf)] for suf in DE_ADJ_ENDINGS if word.endswith(suf)),
        word,
    )


def map_demonym_to_country(entity: str) -> str | None:
    # nationality adjectives to country names
    # e.g. russian -> Russia

    if entity in DEMONYM_TO_COUNTRY_EN:
        return DEMONYM_TO_COUNTRY_EN[entity]

    if entity in DEMONYM_TO_COUNTRY_DE:
        return DEMONYM_TO_COUNTRY_DE[entity]

    normalized_entity = normalize_de_demonym_form(entity)
    if normalized_entity in DEMONYM_TO_COUNTRY_DE:
        return DEMONYM_TO_COUNTRY_DE[normalized_entity]

    if entity.endswith("en"):
        cand = f"{entity[:-2]}e"
        if cand in DEMONYM_TO_COUNTRY_DE:
            return DEMONYM_TO_COUNTRY_DE[cand]

    if entity.endswith("innen"):
        cand = entity[: -len("innen")]
        if cand in DEMONYM_TO_COUNTRY_DE:
            return DEMONYM_TO_COUNTRY_DE[cand]
        stem = cand[:-2] if cand.endswith("er") else cand
        adj = (stem[:-1] if stem.endswith("i") else stem) + "isch"
        if adj in DEMONYM_TO_COUNTRY_DE:
            return DEMONYM_TO_COUNTRY_DE[adj]

    if entity.endswith("er"):
        stem = entity[:-2]
        if stem in DEMONYM_TO_COUNTRY_DE:
            return DEMONYM_TO_COUNTRY_DE[stem]
        adj = (stem[:-1] if stem.endswith("i") else stem) + "isch"
        if adj in DEMONYM_TO_COUNTRY_DE:
            return DEMONYM_TO_COUNTRY_DE[adj]

    return None


def deduplication(entities: list[dict]) -> list[dict]:
    # remove duplicates with different casing from same category
    unique = {}
    for e in entities:
        key = (normalize(e["text"]), e["label"])
        if key not in unique:
            unique[key] = e
        elif e["text"][0].isupper() and not unique[key]["text"][0].isupper():
            unique[key] = e
    return list(unique.values())


def drop_demonyms(entities: list[dict]) -> list[dict]:
    # if both a country name and its demonym exist (e.g. Russia and russian)
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
    if not entities:
        return []

    prepped = []
    heads = []
    for e in entities:
        text = e["text"]
        if toks := tokenize_name(text):
            prefix = " ".join(toks[:-1]).lower()
            head = toks[-1]
        else:
            prefix = ""
            head = text
        prepped.append((e, prefix, head))
        heads.append(head)

    # Compute singular/lemma for heads
    head_to_lemma: dict[str, str] = {}

    if language.lower().startswith("de") and NLP_DE is not None:
        # batched lemmatization via spaCy
        for head_tok, doc in zip(heads, NLP_DE.pipe(heads, batch_size=256)):
            if doc and len(doc) > 0:
                lemma = doc[0].lemma_ or head_tok
                # keep capitalization for German nouns if input looked capitalized
                if head_tok[:1].isupper() and lemma.islower():
                    lemma = lemma.capitalize()
                head_to_lemma[head_tok] = lemma
            else:
                head_to_lemma[head_tok] = head_tok
    else:
        # English or DE fallback: use inflect (EN) or your existing singularize_word
        for head_tok in heads:
            if language.lower().startswith("en"):
                singular = INFLECT.singular_noun(head_tok)
                head_to_lemma[head_tok] = singular or head_tok
            else:
                # fallback to your singularize_word for other langs / DE without spaCy
                head_to_lemma[head_tok] = singularize_word(head_tok, language)

    groups: dict[tuple[str, str], list[dict]] = {}
    for e, prefix, head in prepped:
        lemma = head_to_lemma.get(head, head)
        key = (prefix, lemma.lower())
        groups.setdefault(key, []).append(e)

    cleaned = []
    for key, members in groups.items():
        if len(members) == 1:
            cleaned.append(members[0])
            continue

        lemma_lower = key[1]
        ranked = []
        for e in members:
            toks = tokenize_name(e["text"])
            head = (toks[-1] if toks else e["text"]).lower()
            exact = int(head == lemma_lower)
            ranked.append((exact, -len(head), len(e["text"]), e))
        ranked.sort(reverse=True)
        cleaned.append(ranked[0][3])

    cleaned_idx = {e["idx"] for e in cleaned}
    return [e for e in entities if e["idx"] in cleaned_idx]


def clean_entities(entities: list[dict], lang: str = "en") -> list[dict[str, str]]:
    cleaned_ents = [{**e, "idx": e.get("idx", id(e))} for e in entities if e.get("text", "").strip()]

    cleaned_ents = deduplication(cleaned_ents)
    cleaned_ents = drop_demonyms(cleaned_ents)
    cleaned_ents = deduplicate_persons(cleaned_ents)
    cleaned_ents = singularize(cleaned_ents, lang)

    # return the cleaned entities in their original form
    keep = {e["idx"] for e in cleaned_ents}
    return [e for e in entities if e.get("idx", id(e)) in keep]
