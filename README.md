# city-report-ai-assistance-service

AI Assistance Service for the Urban Issue Platform. This service manages locality prompts, prompt suggestions, and asynchronous AI comment generation.

## Prerequisites

- Python 3.11+
- Docker (for PostgreSQL and Kafka)

## Local infrastructure

Start the dependencies with Docker:

```bash
docker compose up -d
```

## Configuration

Copy the environment template and update values:

```bash
cp .env.example .env
```

## Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Run the service

```bash
uvicorn ai_assistance_service.main:app --app-dir src --host 0.0.0.0 --port 8000
```

## Run tests

```bash
pytest
```
