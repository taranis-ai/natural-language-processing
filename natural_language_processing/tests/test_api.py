import pytest
from flask import Flask
import json

# Import your Flask app here. Adjust as needed.
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

def test_root_health(client):
    response = client.post("/", json={"text": "Health check text."})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)

def test_empty_input(client):
    response = client.post("/", json={"text": ""})
    assert response.status_code == 200
    data = response.get_json()
    # Should probably return empty dict or similar
    assert isinstance(data, dict)
    assert len(data) == 0 or data == {}  # Adjust as per your actual API behavior

def test_invalid_json(client):
    response = client.post("/", data="notjson", content_type="application/json")
    assert response.status_code in (400, 422)  # Adjust for your error handling