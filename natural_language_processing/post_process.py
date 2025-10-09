import re
import simplemma
from collections import defaultdict
import requests

from natural_language_processing.log import logger


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


def dbpedia_lookup(entity_name: str, top_n: int = 5, score_threshold: int = 1000, timeout: float = 10.0) -> set[str] | None:
    # Query DBPedia for the entity name and get the top n results as a set
    # drop results with score < score_threshold

    url = "https://lookup.dbpedia.org/api/search"
    headers = {"Accept": "application/json", "Accept-Language": "en,de;q=0.8", "User-Agent": "python-requests-dbplookup/1.0"}
    params = {"query": entity_name, "maxResults": max(1, top_n), "format": "json"}

    try:
        logger.debug(f"Query DBPedia for entity {entity_name}")
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        resp.raise_for_status()
    except TimeoutError:
        logger.error(f"DBPedia query for {entity_name} timed out")
        return set()
    except requests.exceptions.HTTPError as e:
        logger.error(f"DBPedia query for {entity_name} failed: {e}")
        return set()

    try:
        data = resp.json()
        docs = data.get("docs", [])[:top_n]
        results = []
        for doc in docs:
            result = {"uri": (doc.get("resource") or [None])[0], "score": (doc.get("score") or [None])[0]}
            if result["uri"] is None or result["score"] is None:
                continue
            results.append(result)

        return {doc["uri"] for doc in results if float(doc["score"]) > score_threshold}

    except ValueError:
        logger.error(f"DBPedia query for {entity_name} failed: Could not parse results")
    return set()


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


def deduplicate_by_linking(entities: list[dict]) -> list[dict]:
    # try to match entities to external DBPedia resources
    # if multiple entities map to the same resource, keep only the longest

    linked_entity_idx = {}
    keep_idcs = []

    for i, entity in enumerate(entities):
        linked_entities = dbpedia_lookup(normalize(entity["text"])) or set()

        # could not map entity to DBPedia resource, leave entity as is
        if not linked_entities:
            keep_idcs.append(i)
            continue

        for linked_entity in linked_entities:
            if linked_entity not in linked_entity_idx:
                linked_entity_idx[linked_entity] = i
            else:
                current_best_idx = linked_entity_idx[linked_entity]
                # keep longest entity
                if len(entity["text"]) > len(entities[current_best_idx]["text"]):
                    linked_entity_idx[linked_entity] = i

    kept_indices = set(keep_idcs) | set(linked_entity_idx.values())
    return [entities[i] for i in range(len(entities)) if i in kept_indices]


def clean_entities(entities: list[dict], text: str) -> list[dict[str, str]]:
    cleaned_ents = [{**e, "idx": e.get("idx", id(e))} for e in entities if e.get("text", "").strip()]

    cleaned_ents = remove_leading_trailing_punctuation(cleaned_ents)
    cleaned_ents = deduplication(cleaned_ents)
    cleaned_ents = drop_demonyms(cleaned_ents)
    cleaned_ents = deduplicate_persons(cleaned_ents)
    cleaned_ents = deduplicate_by_lemma(cleaned_ents, text)
    cleaned_ents = deduplicate_by_linking(cleaned_ents)

    # return the cleaned entities in their original form
    keep = {e["idx"] for e in cleaned_ents}
    return [e for e in entities if e.get("idx", id(e)) in keep]
