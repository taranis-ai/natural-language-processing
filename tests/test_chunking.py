import pytest

from natural_language_processing.chunking import split_text_into_chunks


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
