import pytest

from natural_language_processing.chunking import deduplicate_chunk_entities, offset_entity_positions, split_text_into_chunks
from natural_language_processing.config import Config
from natural_language_processing.gliner import Gliner


def test_split_text_into_chunks_returns_single_chunk_for_short_text():
    text = "Berlin is the capital of Germany."

    assert split_text_into_chunks(text, chunk_length=50, chunk_overlap=10) == [(0, text)]


def test_split_text_into_chunks_prefers_whitespace_boundaries():
    text = "Berlin is the capital of Germany and Vienna is the capital of Austria."

    assert split_text_into_chunks(text, chunk_length=30, chunk_overlap=8) == [
        (0, "Berlin is the capital of"),
        (16, "pital of Germany and Vienna"),
        (35, "d Vienna is the capital of"),
        (53, "pital of Austria."),
    ]


def test_offset_entity_positions_offsets_character_spans():
    entities = [
        {"text": "Germany", "label": "Location", "start": 9, "end": 16},
        {"text": "Vienna", "label": "Location"},
    ]

    assert offset_entity_positions(entities, chunk_start=100) == [
        {"text": "Germany", "label": "Location", "start": 109, "end": 116},
        {"text": "Vienna", "label": "Location"},
    ]


def test_deduplicate_chunk_entities_keeps_highest_score_for_exact_duplicates():
    entities = [
        {"text": "Germany", "label": "Location", "start": 24, "end": 31, "score": 0.82},
        {"text": "Germany", "label": "Location", "start": 24, "end": 31, "score": 0.91},
        {"text": "Vienna", "label": "Location", "start": 36, "end": 42, "score": 0.87},
    ]

    assert deduplicate_chunk_entities(entities, text_key="text", label_key="label") == [
        {"text": "Germany", "label": "Location", "start": 24, "end": 31, "score": 0.91},
        {"text": "Vienna", "label": "Location", "start": 36, "end": 42, "score": 0.87},
    ]


def test_deduplicate_chunk_entities_is_case_insensitive_for_text():
    entities = [
        {"text": "Berlin", "label": "Location", "start": 0, "end": 6, "score": 0.88},
        {"text": "berlin", "label": "Location", "start": 0, "end": 6, "score": 0.92},
    ]

    assert deduplicate_chunk_entities(entities, text_key="text", label_key="label") == [
        {"text": "berlin", "label": "Location", "start": 0, "end": 6, "score": 0.92},
    ]


@pytest.mark.asyncio
async def test_gliner_general_model_processes_text_in_chunks():
    original_chunk_length = Config.TEXT_CHUNK_LENGTH
    original_chunk_overlap = Config.TEXT_CHUNK_OVERLAP
    Config.TEXT_CHUNK_LENGTH = 30
    Config.TEXT_CHUNK_OVERLAP = 8

    calls = []

    class FakeModel:
        def predict_entities(self, chunk_text: str, labels: list[str], threshold: float):
            calls.append(chunk_text)
            if "Germany" in chunk_text:
                start = chunk_text.index("Germany")
                return [{"text": "Germany", "label": "Location", "start": start, "end": start + len("Germany"), "score": 0.91}]
            return []

    try:
        model = Gliner.__new__(Gliner)
        model.general_model = FakeModel()
        model.general_labels = ["Location"]
        model.cybersec_model = FakeModel()
        model.cybersec_labels = []

        result = await model._predict_chunked(
            model.general_model,
            "Berlin is the capital of Germany and Vienna is the capital of Austria.",
            model.general_labels,
        )
    finally:
        Config.TEXT_CHUNK_LENGTH = original_chunk_length
        Config.TEXT_CHUNK_OVERLAP = original_chunk_overlap

    assert len(calls) > 1
    assert result == [{"text": "Germany", "label": "Location", "start": 25, "end": 32, "score": 0.91}]


@pytest.mark.parametrize(
    "chunk_length,chunk_overlap",
    [
        (0, 0),
        (10, -1),
        (10, 10),
    ],
)
def test_split_text_into_chunks_validates_arguments(chunk_length, chunk_overlap):
    with pytest.raises(ValueError):
        split_text_into_chunks("text", chunk_length=chunk_length, chunk_overlap=chunk_overlap)
