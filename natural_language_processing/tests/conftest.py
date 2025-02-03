import os
import pytest
import json

from natural_language_processing.roberta_ner import RobertaNER
from natural_language_processing.flair_ner import FlairNER


@pytest.fixture(scope="session")
def news_items():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    story_json = os.path.join(dir_path, "story_list.json")
    with open(story_json) as f:
        data = json.load(f)
    yield [item["content"] for cluster in data for item in cluster["news_items"] if "content" in item]


@pytest.fixture(scope="session")
def flair_analyzer():
    yield FlairNER()


@pytest.fixture(scope="session")
def roberta_analyzer():
    yield RobertaNER()


@pytest.fixture(scope="session")
def example_text():
    yield "This is an example for NER, about the ACME Corporation which is producing Dynamite in Acme City, which is in Australia and run by Mr. Wile E. Coyote"
