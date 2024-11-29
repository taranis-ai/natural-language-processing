FROM python:3.10

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    cmake \
    gcc \
    g++ \
    git \
    pkg-config \
    libsentencepiece-dev \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r /app/requirements.txt

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "your_application_entrypoint.py"]
