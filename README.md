# HCC Documentation Automation Pipeline

[![CI/CD](https://github.com/yourusername/hcc-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/hcc-pipeline/actions)

## Overview

The **HCC Documentation Automation Pipeline** automates the extraction and validation of Hierarchical Condition Categories (HCC) codes from clinical notes. This pipeline integrates AI models, LangGraph-powered workflow management, and scalable batch processing to streamline healthcare coding tasks.

## Features
- **Automated HCC code extraction** from clinical notes
- **LangGraph-powered workflow management** for dynamic state machines
- **Scalable batch processing** for handling large datasets
- **Dockerized deployment** for ease of setup and scaling
- **REST API endpoints** for system integration and management

## Setup

### Prerequisites
- **Poetry** for dependency management and virtual environment handling
- **Docker** (optional, for containerized deployment)

## Docker Setup

### Prerequisites
- Docker installed
- Docker Compose (optional)

### Quick Start
```bash
# Build the Docker image
docker build -t hcc-pipeline .

# Run the container with volume mounts and env file
docker run -it --rm \
  --env-file .docker.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  hcc-pipeline
```

## Installation and Local Development

```bash
# Install Poetry if not already installed
pip install poetry

# Install project dependencies
poetry install

# Run the API server with auto-reload for development
poetry run uvicorn hcc_pipeline.api.app:app --reload
```

## Debugging & Development

```bash
# Install dev tools
poetry install --with dev

# Run the main pipeline
poetry run python -m hcc_pipeline.main

# Start LangGraph development server
poetry run langgraph dev --config langgraph.json

# Build the Docker image
docker build -t hcc-pipeline .

# Run the container with volume mounts and env file
docker run -it --rm \
  --env-file .docker.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  hcc-pipeline
```

## Project Structure

```
hcc-pipeline/
├── .env.example
├── pyproject.toml
├── poetry.lock
├── Dockerfile
├── docker-compose.yml
├── langgraph.json
└── README.md
```

| File/Folder            | Description                                        |
|-----------------|--------------------------------------------------|
| `.env`                 | Template for environment variables                  |
| `pyproject.toml`       | Poetry configuration for dependency management     |
| `poetry.lock`          | Dependency lock file                               |
| `Dockerfile`           | Docker configuration                              |
| `docker-compose.yml`   | Multi-container setup configuration                |
| `langgraph.json`       | LangGraph configuration                           |
| `README.md`            | Project documentation                            |

### Source Code (`src/`)

```
src/
└── hcc_pipeline/
    ├── __init__.py
    ├── main.py
    ├── core/
    │   ├── __init__.py
    │   ├── extraction.py
    │   └── evaluation.py
    ├── workflows/
    │   ├── __init__.py
    │   └── hcc_workflow.py
    ├── utils/
    │   ├── __init__.py
    │   ├── file_handlers.py
    │   └── logging.py
    └── api/
        ├── __init__.py
        └── app.py
```

### Core Components

| File/Module              | Purpose                                      |
|----------------|------------------------------------------|
| `main.py`                | Orchestrates the pipeline                    |
| `core/extraction.py`     | Extracts HCC codes from clinical notes       |
| `core/evaluation.py`     | Validates extracted HCC codes               |

### Workflow Management

| File/Module                  | Purpose                                      |
|-------------------|----------------------------------------|
| `workflows/hcc_workflow.py`   | Defines LangGraph state machine              |

### Utilities

| File/Module                  | Purpose                                      |
|----------------|------------------------------------------|
| `utils/file_handlers.py`     | Handles file I/O operations                  |
| `utils/logging.py`           | Configures logging for the pipeline          |

### API Layer

| File/Module                  | Purpose                                      |
|----------------|------------------------------------------|
| `api/app.py`                 | FastAPI implementation for REST API endpoints |

## Data Directory (`data/`)

```
data/
├── progress_notes/
│   ├── pn_1
│   ├── pn_2
│   └── ...
└── hcc_codes.csv
```

| File/Folder                | Purpose                                      |
|----------------|----------------------------------------|
| `progress_notes/`          | Contains clinical notes                     |
| `hcc_codes.csv`            | CSV file with HCC-relevant codes           |

## Tests Directory (`tests/`)

```
tests/
├── unit/
│   ├── test_extraction.py
│   └── test_evaluation.py
└── integration/
    └── test_pipeline.py
```

| File/Folder              | Purpose                                      |
|----------------|----------------------------------------|
| `test_extraction.py`     | Unit tests for extraction logic            |
| `test_evaluation.py`     | Unit tests for HCC code validation         |
| `test_pipeline.py`       | Integration tests for the full pipeline    |

## Docker Configuration (`docker/`)

```
docker/
└── credentials/
    └── service-account.json
```

| File/Folder              | Purpose                                      |
|----------------|----------------------------------------|
| `credentials/`           | Stores sensitive credentials                |

## Output Directory (`output/`)

```
output/
└── hcc_results.json
```

| File                | Purpose                                      |
|----------------|----------------------------------------|
| `hcc_results.json`  | Final output with extracted conditions      |

## CI/CD Configuration (`.github/`)

```
.github/
└── workflows/
    └── tests.yml
```

| File               | Purpose                                      |
|----------------|----------------------------------------|
| `tests.yml`        | GitHub Actions configuration                |

## Key Implementation Files

### `core/extraction.py`

```python
def extract_conditions(text: str) -> List[Dict]:
    """Uses AI to extract medical conditions and codes"""
```

### `workflows/hcc_workflow.py`

```python
class PipelineState(TypedDict):
    """Defines data structure for workflow processing"""
```

### `utils/file_handlers.py`

```python
def read_input_files(input_dir: str) -> Dict[str, str]:
    """Reads all clinical notes from directory"""
```

---