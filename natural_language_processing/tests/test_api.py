import pytest
from app import app as flask_app
from natural_language_processing.config import Config

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@pytest.fixture
def client_with_api_key(monkeypatch):
    """Client with API key authentication enabled"""
    # Temporarily set API key for testing
    monkeypatch.setenv('API_KEY', 'test-api-key-123')
    
    # Reload config to pick up the new API key
    Config.API_KEY = 'test-api-key-123'
    
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
    assert response.status_code == 400
    data = response.get_json()
    assert isinstance(data, dict)
    assert data["error"] == "No text provided for NER extraction"

def test_invalid_json(client):
    response = client.post("/", data="notjson", content_type="application/json")
    assert response.status_code == 400

def test_valid_json_but_not_dict(client):
    """Test valid JSON that isn't a dictionary"""
    # This mimics: curl -d '"notjson"' (valid JSON string, not a dict)
    response = client.post("/", data='"notjson"', content_type="application/json")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_missing_authorization_header_with_api_key(client_with_api_key):
    """Test missing Authorization header when API key is required"""
    response = client_with_api_key.post("/", json={"text": "test"})
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "not authorized"

def test_malformed_authorization_header_syntax(client_with_api_key):
    """Test malformed Authorization header - the exact issue you encountered"""
    # This mimics: curl -H "Authorization Bearer: test-api-key-123" (missing colon after Authorization)
    headers = {"Authorization Bearer": "test-api-key-123"}
    response = client_with_api_key.post("/", json={"text": "test"}, headers=headers)
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "not authorized"

def test_malformed_authorization_header_no_bearer(client_with_api_key):
    """Test Authorization header without Bearer prefix"""
    headers = {"Authorization": "test-api-key-123"}  # Missing "Bearer " prefix
    response = client_with_api_key.post("/", json={"text": "test"}, headers=headers)
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "not authorized"

def test_correct_authorization_header(client_with_api_key):
    """Test correct Authorization header format"""
    headers = {"Authorization": "Bearer test-api-key-123"}
    response = client_with_api_key.post("/", json={"text": "test"}, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)

def test_wrong_api_key(client_with_api_key):
    """Test wrong API key"""
    headers = {"Authorization": "Bearer wrong-api-key"}
    response = client_with_api_key.post("/", json={"text": "test"}, headers=headers)
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "not authorized"