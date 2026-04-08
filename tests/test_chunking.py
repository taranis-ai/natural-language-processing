import pytest

from natural_language_processing.chunking import split_text_into_chunks


def test_split_text_into_chunks_returns_single_chunk_for_short_text():
    assert split_text_into_chunks("short text", chunk_length=20, chunk_overlap=5) == [(0, "short text")]


def test_split_text_into_chunks_prefers_whitespace_boundaries():
    text = "alpha beta gamma delta epsilon"

    assert split_text_into_chunks(text, chunk_length=12, chunk_overlap=3) == [
        (0, "alpha beta"),
        (7, "eta gamma"),
        (13, "mma delta"),
        (19, "lta epsilon"),
    ]


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
