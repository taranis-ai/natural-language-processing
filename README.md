# Taranis AI NLP Bot

Performs natural language processing on news items, extracting keywords and named entities for better topic tagging and content analysis

## Development

```bash
uv venv
uv sync --all-extras --dev
```

## Usage

Run via

```bash
flask run
# or
granian run
# or
docker run -p 8000:8000 ghcr.io/taranis-ai/taranis-nlp-bot:latest
```

### Example API Call

To test the API with a POST request, use curl:

```bash
curl -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -d '{"text": "This is an example for NER, about the ACME Corporation which is producing Dynamite in Acme City, which is in Australia and run by Mr. Wile E. Coyote."}'
```

```python
import requests

json_data = {
    'text': 'This is an example for NER, about the ACME Corporation which is producing Dynamite in Acme City, which is in Australia and run by Mr. Wile E. Coyote.',
}

response = requests.post('http://127.0.0.1:8000', json=json_data)

print(response.text)
```


## License

EUROPEAN UNION PUBLIC LICENCE v. 1.2
