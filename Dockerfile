FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ".[dev]"

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
