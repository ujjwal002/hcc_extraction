Here's the structured `README.md` for your HCC Documentation Automation Pipeline:

```markdown
# HCC Documentation Automation Pipeline

[![CI/CD](https://github.com/yourusername/hcc-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/hcc-pipeline/actions)

## Overview

The **HCC Documentation Automation Pipeline** automates the extraction and validation of Hierarchical Condition Categories (HCC) codes from clinical notes. This pipeline integrates AI models, LangGraph-powered workflow management, and scalable batch processing to streamline healthcare coding tasks.

### Features
- **Automated HCC code extraction** from clinical notes
- **LangGraph-powered workflow management** for dynamic state machines
- **Scalable batch processing** for handling large datasets
- **Dockerized deployment** for ease of setup and scaling
- **REST API endpoints** for system integration and management

## Setup

### Prerequisites
- **Poetry** for dependency management and virtual environment handling
- **Docker** (optional, for containerized deployment)

### Installation and Local Development

1. **Install Poetry**:
   ```bash
   pip install poetry
   ```

2. **Run the API server** (with auto-reload for development):
   ```bash
   poetry run uvicorn hcc_pipeline.api.app:app --reload
   ```

3. **Run the main pipeline**:
   ```bash
   poetry run python -m hcc_pipeline.main
   ```

4. **Start LangGraph development server**:
   ```bash
   poetry run langgraph dev --config langgraph.json
   ```

---

### Project Structure

The project follows best practices for modularity, scalability, and testability. Below is a breakdown of the key directories and files:

#### Project Root Directory
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

| File/Folder            | Description                                                                            |
|------------------------|----------------------------------------------------------------------------------------|
| `.env`                 | Template for environment variables (e.g., API keys, paths)                            |
| `pyproject.toml`       | Poetry configuration for dependency management                                        |
| `poetry.lock`          | Dependency lock file generated by Poetry                                              |
| `Dockerfile`           | Docker configuration for building the container                                        |
| `docker-compose.yml`   | Multi-container setup configuration (e.g., for additional services like databases)     |
| `langgraph.json`       | Configuration for LangGraph development server                                        |
| `README.md`            | Project documentation and usage guide                                                 |

---

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

#### Core Components

| File/Module              | Purpose                                                                 |
|--------------------------|-------------------------------------------------------------------------|
| `main.py`                | Orchestrates the entire pipeline                                       |
| `core/extraction.py`     | Extracts HCC codes from clinical notes using AI model integration       |
| `core/evaluation.py`     | Validates extracted HCC codes and filters based on relevance           |

#### Workflow Management

| File/Module                  | Purpose                                                              |
|------------------------------|----------------------------------------------------------------------|
| `workflows/hcc_workflow.py`   | Defines LangGraph state machine and processing nodes                  |

#### Utilities

| File/Module                  | Purpose                                                              |
|------------------------------|----------------------------------------------------------------------|
| `utils/file_handlers.py`     | Handles file I/O operations (reading and saving notes)               |
| `utils/logging.py`           | Configures logging for the pipeline                                  |

#### API Layer

| File/Module                  | Purpose                                                              |
|------------------------------|----------------------------------------------------------------------|
| `api/app.py`                 | FastAPI implementation for REST API endpoints                        |

---

### Data Directory (`data/`)

```
data/
├── progress_notes/
│   ├── pn_1
│   ├── pn_2
│   └── ...
└── hcc_codes.csv
```

| File/Folder                | Purpose                                                                 |
|----------------------------|-------------------------------------------------------------------------|
| `progress_notes/`          | Contains clinical notes in text format (one file per patient)          |
| `hcc_codes.csv`            | CSV file with HCC-relevant ICD-10 codes and descriptions               |

---

### Tests Directory (`tests/`)

```
tests/
├── unit/
│   ├── test_extraction.py
│   └── test_evaluation.py
└── integration/
    └── test_pipeline.py
```

| File/Folder              | Purpose                                                                |
|--------------------------|------------------------------------------------------------------------|
| `test_extraction.py`     | Unit tests for condition extraction logic                              |
| `test_evaluation.py`     | Unit tests for HCC code validation                                     |
| `test_pipeline.py`       | Integration tests for the full pipeline execution                      |

---

### Docker Configuration (`docker/`)

```
docker/
└── credentials/
    └── service-account.json
```

| File/Folder              | Purpose                                                                |
|--------------------------|------------------------------------------------------------------------|
| `credentials/`           | Stores sensitive credentials (e.g., service account keys)              |

---

### Output Directory (`output/`)

```
output/
└── hcc_results.json
```

| File                | Purpose                                                                 |
|---------------------|-------------------------------------------------------------------------|
| `hcc_results.json`  | Final output containing extracted conditions and corresponding HCC codes|

---

### CI/CD Configuration (`.github/`)

```
.github/
└── workflows/
    └── tests.yml
```

| File               | Purpose                                                                |
|--------------------|------------------------------------------------------------------------|
| `tests.yml`        | GitHub Actions configuration for automated testing                     |

---

### Key Implementation Files

#### 1. `core/extraction.py`

```python
def extract_conditions(text: str) -> List[Dict]:
    """Uses Gemini AI to extract medical conditions and codes from clinical notes"""
    # AI model integration
    # JSON response parsing
    # Error handling
```

#### 2. `workflows/hcc_workflow.py`

```python
class PipelineState(TypedDict):
    """Defines data structure for workflow processing"""
    note_text: str
    hcc_codes: Set[str]
    conditions: List[Dict]
    hcc_relevant: List[Dict]

def create_hcc_workflow():
    """Builds LangGraph state machine with nodes and edges"""
```

#### 3. `utils/file_handlers.py`

```python
def read_input_files(input_dir: str) -> Dict[str, str]:
    """Reads all clinical notes from directory"""
    # File validation
    # Text normalization

def save_output(results: Dict, output_dir: str):
    """Saves processing results to JSON"""
    # Output validation
    # File versioning
```

---
