# HCC Documentation Automation Pipeline

[![CI/CD](https://github.com/yourusername/hcc-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/hcc-pipeline/actions)

## Features
- Automated HCC code extraction from clinical notes
- LangGraph-powered workflow management
- Scalable batch processing
- Dockerized deployment
- REST API endpoints

## Setup

### Local Development
1. Install Poetry
```bash
pip install poetry

poetry run uvicorn hcc_pipeline.api.app:app --reload 

poetry run python -m hcc_pipeline.main  