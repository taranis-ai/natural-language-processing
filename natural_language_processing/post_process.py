import re
import simplemma
from collections import defaultdict

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


def map_entity_types(entity_type: str) -> str:
    # map entity types ORG, LOC, PER ->
    # Organization, Location, Person resp.
    entity_type_map = {"ORG": "Organization", "LOC": "Location", "PER": "Person", "MISC": "Misc"}
    return entity_type_map.get(entity_type, entity_type)


def is_entity_allowed(entity_type: str, allowed_entities: list[str]) -> bool:
    return entity_type.lower() in [ent.lower() for ent in allowed_entities]


def normalize(s: str) -> str:
    # remove whitespaces and cast to lowercase
    # " Marty   Friedman"  -> "marty friedman"
    return re.sub(r"\s+", " ", s).strip().lower()


def tokenize_name(name: str) -> list[str]:
    # split on whitespace and simple punctuation
    # "ralf schumacher" -> ["ralf", "schumacher"]
    return [t for t in re.split(r"[^\wÀ-ÖØ-öø-ÿ]+", name) if t]


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


def remove_leading_trailing_punctuation(entities: list[dict]) -> list[dict]:
    cleaned_entities = []
    for entity in entities:
        clean_entity_text = re.sub(r"(^[\s.,!;?]+|[\s.,!;?]+$)", "", entity["text"], flags=re.UNICODE)
        cleaned_entities.append({**entity, "text": clean_entity_text})
    return cleaned_entities


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
        if e.get("label") != "Location":
            continue
        ent_txt = normalize(e["text"])
        country = map_demonym_to_country(ent_txt)
        if country and country in texts:
            to_drop_idcs.add(id(e))

    return [e for e in entities if id(e) not in to_drop_idcs]


def deduplicate_persons(entities: list[dict]) -> list[dict]:
    # if a person is mentioned twice in a text (e.g. Willem Defoe & Defoe)
    # -> drop the entity with only the last name

    persons = [e for e in entities if e["label"] == "Person"]
    single_word_list = []
    multi_word_list = []

    # split persons into single-word and multi-word (e.g. "Defoe" & "Willem Defoe")
    for p in persons:
        tokens = tokenize_name(normalize(p["text"]))
        if len(tokens) >= 2:
            multi_word_list.append((p, tokens))
        else:
            single_word_list.append((p, tokens))

    to_drop_idcs = set()

    # for each single-word entity, check if it is contained in any of the multi-word entities
    for single_word_entity, single_word_tokens in single_word_list:
        s = single_word_tokens[0] if single_word_tokens else ""
        if not s:
            continue
        for _, multi_tokens in multi_word_list:
            if any(t == s for t in multi_tokens):
                to_drop_idcs.add(id(single_word_entity))
                break
    return [e for e in entities if id(e) not in to_drop_idcs]


def deduplicate_by_lemma(entities: list[dict], text: str) -> list[dict]:
    # check if multiple entities of the same "label" share the same lemma
    # if yes, and the lemma is also in the text use the lemmatized form
    # otherwise keep the shortest entity
    # e.g.: LEDs -> LED, mouse & mice -> mouse, Palästen & Paläste -> Paläste (if Palast not in text)

    duplicate_candidates = defaultdict(list)
    cleaned_entities = []

    # group entities by label and lemma
    for entity in entities:
        entity_text = entity["text"]

        # need to tokenize entity, because simplemma cannot handle multi-word entities (e.g. "apple stores")
        lemma = " ".join([simplemma.lemmatize(token, lang=("de", "en")) for token in tokenize_name(entity_text)])
        duplicate_candidates[(lemma, entity["label"])].append(entity)

    for (lemma, _), duplicate_entities in duplicate_candidates.items():
        if len(duplicate_entities) == 1:
            entity = duplicate_entities[0]
        else:
            entity = min(duplicate_entities, key=lambda entity: len(entity["text"]))

        if lemma in text:
            cleaned_entities.append({**entity, "text": lemma})
        else:
            cleaned_entities.append(entity)

    return cleaned_entities


def clean_entities(entities: list[dict], text: str) -> list[dict[str, str]]:
    cleaned_ents = [{**e, "idx": e.get("idx", id(e))} for e in entities if e.get("text", "").strip()]

    cleaned_ents = remove_leading_trailing_punctuation(cleaned_ents)
    cleaned_ents = deduplication(cleaned_ents)
    cleaned_ents = drop_demonyms(cleaned_ents)
    cleaned_ents = deduplicate_persons(cleaned_ents)
    cleaned_ents = deduplicate_by_lemma(cleaned_ents, text)

    # return the cleaned entities in their original form
    keep = {e["idx"] for e in cleaned_ents}
    return [e for e in entities if e.get("idx", id(e)) in keep]
