FROM python:3.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . .

VOLUME /app/data /app/output
ENV GEMINI_API_KEY="AIzaSyB6-olSp5r5EbsWR5vEsK0OnVycQcC1yI0"

CMD ["python", "-m", "hcc_pipeline.main"]