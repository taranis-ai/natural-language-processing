import re
from typing import Any


def split_text_into_chunks(text: str, chunk_length: int, chunk_overlap: int) -> list[tuple[int, str]]:
    if chunk_length <= 0:
        raise ValueError("chunk_length must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_length:
        raise ValueError("chunk_overlap must be smaller than chunk_length")

    if len(text) <= chunk_length:
        return [(0, text)]

    chunks: list[tuple[int, str]] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        hard_end = min(start + chunk_length, text_length)
        end = hard_end

        if hard_end < text_length:
            # Prefer to end on whitespace so we avoid cutting most words in half.
            for match in re.finditer(r"\s+", text[start:hard_end]):
                end = start + match.start()

        if end <= start:
            end = hard_end

        chunks.append((start, text[start:end]))
        if end >= text_length:
            break

        start = max(end - chunk_overlap, start + 1)

    return chunks


def offset_entity_positions(entities: list[dict[str, Any]], chunk_start: int) -> list[dict[str, Any]]:
    offset_entities = []
    for entity in entities:
        start = entity.get("start")
        end = entity.get("end")

        if isinstance(start, int) and isinstance(end, int):
            offset_entities.append({**entity, "start": start + chunk_start, "end": end + chunk_start})
        else:
            offset_entities.append(entity)

    return offset_entities


def deduplicate_chunk_entities(entities: list[dict[str, Any]], text_key: str, label_key: str) -> list[dict[str, Any]]:
    unique_entities: dict[tuple[Any, Any, str, str], dict[str, Any]] = {}

    for entity in entities:
        key = (
            entity.get("start"),
            entity.get("end"),
            str(entity.get(text_key, "")).strip().lower(),
            str(entity.get(label_key, "")),
        )
        current = unique_entities.get(key)
        if current is None or float(entity.get("score", 0.0)) > float(current.get("score", 0.0)):
            unique_entities[key] = entity

    return sorted(unique_entities.values(), key=lambda entity: (entity.get("start", -1), entity.get("end", -1)))
