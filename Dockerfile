# Build Stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.7.0

# Copy only necessary files to install dependencies
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Runtime Stage
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed dependencies from the build stage
COPY --from=builder /app /app

# Copy application files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app \
    INPUT_DIR=/app/data/progress_notes \
    HCC_CSV_PATH=/app/data/hcc_codes.csv \
    OUTPUT_DIR=/app/output

# Define volumes for input/output
VOLUME /app/data
VOLUME /app/output

# Default command to run the application
CMD ["python", "-m", "hcc_pipeline.main"]
