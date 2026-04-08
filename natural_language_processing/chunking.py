import re


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
