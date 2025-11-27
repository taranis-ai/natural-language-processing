# Taranis AI natural-language-processing Bot

Bot for extracting named entities (e.g. Location, Person, etc.) from texts.
Available models:
- gliner (+ cybersec gliner) (https://huggingface.co/llinauer/gliner_de_en_news) - *Default*
- roberta (https://huggingface.co/FacebookAI/xlm-roberta-large-finetuned-conll03-english)
- roberta_german (https://huggingface.co/FacebookAI/xlm-roberta-large-finetuned-conll03-german)

The following entities can be extracted:
- Person, Location, Organization (for all three models)
- (+) MISC (for roberta & roberta_german)
- (+) Product, Address
- (+) CLICommand/CodeSnippet, Con, Group, Malware, Sector, Tactic, Technique, Tool

## Pre-requisites

- uv - https://docs.astral.sh/uv/getting-started/installation/
- docker (for building container) - https://docs.docker.com/engine/

Create a python venv and install the necessary packages for the bot to run.

```bash
uv venv
source .venv/bin/activate
uv sync --all-extras --dev
```

## Usage

You can run your bot locally with

```bash
flask run --port 5500
# or
granian app --port 5500
```

You can set configs either via a `.env` file or by setting environment variables directly.
available configs are in the `config.py`
You can select the model via the `MODEL` env var. E.g.:

```bash
MODEL=roberta flask run
```


## Docker

You can also create a Docker image out of this bot. For this, you first need to build the image with the build_container.sh

You can specify which model the image should be built with the MODEL environment variable. If you omit it, the image will be built with the default model.

```bash
MODEL=<model_name> ./build_container.sh
```

then you can run it with:

```bash
docker run -p 5500:8000 <image-name>:<tag>
```

If you encounter errors, make sure that port 5500 is not in use by another application.


## Test the bot

Once the bot is running, you can send test data to it on which it runs its inference method:

```bash
> curl -X POST http://127.0.0.1:5500 -H "Content-Type: application/json" -d '{"text": "This is an example for NER, about the ACME Corporation which is producing Dynamite in Acme City, which is in Australia and run by Mr. Wile E. Coyote"}'
> {"ACME Corporation":"Organization","Acme City":"Location","Australia":"Location","Dynamite":"Product","NER":"Organization","Wile E. Coyote":"Person"}
```

The bot accepts the key `extended_output` in the payload, which causes it to return more information.
```bash
>curl -X POST http://127.0.0.1:5500 -H "Content-Type: application/json" -d '{"text": "This is an example for NER, about the ACME Corporation which is producing Dynamite in Acme City, which is in Australia and run by Mr. Wile E. Coyote", "extended_output": true}'
>[{"position":"23-26","probability":"0.93","type":"Organization","value":"NER"},{"position":"38-54","probability":"1.00","type":"Organization","value":"ACME Corporation"},{"position":"74-82","probability":"0.90","type":"Product","value":"Dynamite"},{"position":"86-95","probability":"0.92","type":"Location","value":"Acme City"},{"position":"109-118","probability":"1.00","type":"Location","value":"Australia"},{"position":"134-148","probability":"0.99","type":"Person","value":"Wile E. Coyote"}]
```

You can also set up authorization via the `API_KEY` env var. In this case, you need to send the API_KEY as an Authorization header:

```bash
> curl -X POST http://127.0.0.1:5500/  -H "Authorization: Bearer api_key" -H "Content-Type: application/json"   -d '{"text": "This is an example for NER, about the ACME Corporation which is producing Dy#namite in Acme City, which is in Australia and run by Mr. Wile E. Coyote."}'
> {"ACME Corporation":"Organization","Acme City":"Location","Australia":"Location","Dynamite":"Product","NER":"Organization","Wile E. Coyote":"Person"}
```

Finally, if you are using the gliner model, you can additionally extract cybersecurity-related entities:

```bash
> curl -X POST http://127.0.0.1:5500 -H "Content-Type: application/json" -d '{"text": "Upon opening Emotet maldocs, victims are greeted with fake Microsoft 365 prompt that states THIS DOCUMENT IS PROTECTED, and instructs victims on how to enable macros.", "cybersecurity": true}'
> {"Emotet":"Malware","Microsoft 365":"Product"}
```

## Development

If you want to contribute to the development of this bot, make sure you set up your pre-commit hooks correctly:

- Install pre-commit (https://pre-commit.com/)
- Setup hooks: `> pre-commit install`


## License

EUROPEAN UNION PUBLIC LICENCE v. 1.2
