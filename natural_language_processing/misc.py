import re


def get_word_positions(text: str, word: str, start_position: int) -> str:
    start_word_pos = len(re.findall(r"\S+", text[:start_position]))
    end_word_pos = start_word_pos + len(word.split())
    return f"{start_word_pos}-{end_word_pos}"
