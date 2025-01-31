FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app/

# install common packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    python3-dev \
    git

COPY . /app/

ENV UV_COMPILE_BYTECODE=1

RUN uv venv && \
    export PATH="/app/.venv/bin:$PATH" && \
    uv sync --frozen

FROM python:3.12-slim

ARG MODEL="flair"

WORKDIR /app/

RUN groupadd user && useradd --home-dir /app -g user user && chown -R user:user /app
RUN install -d -o user -g user /app/data

COPY --from=builder --chown=user:user /app/.venv /app/.venv
COPY --chown=user:user natural_language_processing /app/natural_language_processing
COPY --chown=user:user README.md app.py LICENSE.md /app/

USER user

ENV PYTHONOPTIMIZE=1
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV GRANIAN_THREADS=2
ENV GRANIAN_WORKERS=2
ENV GRANIAN_BLOCKING_THREADS=4
ENV GRANIAN_INTERFACE=wsgi
ENV GRANIAN_HOST=0.0.0.0

# bake models in to the image
RUN python -c 'from natural_language_processing.nlp import NLPProcessor; NLPProcessor()'

EXPOSE 8000

CMD ["granian", "app"]