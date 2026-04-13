---
layout: post
title: "Project Structure with pyproject.toml"
description: "Modern Python packaging — no more setup.py or requirements.txt. Use pyproject.toml for dependencies, tools, and build configuration"
categories: [python-production]
series: python-production
module: 2
module_order: 201
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-project-structure
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Most Python projects still ship with `requirements.txt` + `setup.py` + `setup.cfg` + `MANIFEST.in`. Four files to define one thing: what this project is and what it needs. Some add `Pipfile`, `poetry.lock`, or `conda` files — making it worse.

**The fix:** `pyproject.toml` — one file, everything in it.

## Project Structure

```
python-production-blueprint/
├── pyproject.toml          # Dependencies, tools, build config
├── Dockerfile              # Container image
├── docker-compose.yml      # Dev workflow
├── .env.staging            # Environment variables (dev/staging)
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app entry point
│   ├── config.py           # Settings from environment
│   ├── logging_config.py   # Structured logging setup
│   ├── vault.py            # Vault secret management
│   ├── api/
│   │   ├── models/
│   │   │   └── items.py    # Pydantic request/response models
│   │   └── routes/
│   │       ├── health.py   # Health + readiness endpoints
│   │       └── items.py    # Business logic routes
│   ├── middleware/
│   │   └── logging_middleware.py
│   └── telemetry/
│       ├── metrics.py      # Prometheus metrics
│       └── tracing.py      # OpenTelemetry setup
├── tests/
│   ├── conftest.py         # Shared fixtures
│   └── test_api.py         # API tests
├── infrastructure/         # Observability stack (Vector, Kafka, ES)
├── deploy/                 # Platform-specific deployment configs
└── devsecops/              # Security tooling
```

## pyproject.toml — The Single Source of Truth

```toml
[project]
name = "python-production-blueprint"
version = "0.2.0"
description = "Production-grade FastAPI blueprint with observability"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "structlog>=24.4.0",
    "python-json-logger>=3.2.0",
    "opentelemetry-api>=1.29.0",
    "opentelemetry-sdk>=1.29.0",
    "opentelemetry-instrumentation-fastapi>=0.50b0",
    "opentelemetry-instrumentation-logging>=0.50b0",
    "opentelemetry-exporter-otlp>=1.29.0",
    "opentelemetry-exporter-prometheus>=0.50b0",
    "prometheus-client>=0.21.0",
    "httpx>=0.28.0",
    "hvac>=2.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",
    "ruff>=0.8.0",
    "bandit>=1.8.0",
    "safety>=3.0.0",
    "pip-audit>=2.7.0",
    "pre-commit>=4.0.0",
]

[tool.setuptools.packages.find]
include = ["app*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --tb=short --cov=app --cov-report=term-missing"

[tool.ruff]
target-version = "py311"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "S", "B", "A", "COM", "C4", "DTZ", "T20", "ICN"]
ignore = ["COM812", "S104"]

[tool.bandit]
exclude_dirs = ["tests", ".venv"]
skips = ["B101"]
```

## What Each Section Does

### `[project]` — Package Identity

| Field | Purpose |
|-------|---------|
| `name` | Package name (used by pip, Docker, CI) |
| `version` | Semantic version — update on each release |
| `requires-python` | Minimum Python version — 3.11 for performance + `tomllib` |
| `dependencies` | Runtime dependencies — what runs in production |

### `[project.optional-dependencies]` — Dev Tools

```toml
[project.optional-dependencies]
dev = ["pytest>=8.3.0", "ruff>=0.8.0", "bandit>=1.8.0", ...]
```

Install with `pip install -e ".[dev]"`. These packages never deploy to production.

### `[tool.setuptools.packages.find]` — Package Discovery

```toml
[tool.setuptools.packages.find]
include = ["app*"]
```

Without this, setuptools sees `deploy/`, `infrastructure/`, `tests/` as top-level packages and fails. The `include` filter ensures only `app/` is packaged.

### `[tool.pytest.ini_options]` — Test Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"       # No @pytest.mark.asyncio needed
addopts = "-v --tb=short --cov=app --cov-report=term-missing"
```

- `asyncio_mode = "auto"` — pytest-asyncio auto-detects async test functions
- `--cov=app` — Measure coverage for the `app/` package
- `--cov-report=term-missing` — Show which lines aren't covered

### `[tool.ruff]` — Linting

```toml
[tool.ruff]
target-version = "py311"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "S", "B", "A", "COM", "C4", "DTZ", "T20", "ICN"]
```

Ruff replaces flake8, isort, pyupgrade, and bandit's basic checks — in one tool, 100x faster.

## Why Not requirements.txt?

| Feature | requirements.txt | pyproject.toml |
|---------|-----------------|----------------|
| Pin versions | ✅ `==` only | ✅ `>=`, `~=`, ranges |
| Separate dev deps | ❌ Needs second file | ✅ `[project.optional-dependencies]` |
| Tool config | ❌ Separate files | ✅ `[tool.pytest]`, `[tool.ruff]`, etc. |
| Build metadata | ❌ Needs setup.py | ✅ `[project]` section |
| PEP standard | ❌ Convention only | ✅ PEP 621, 517, 518 |

## Next Step

In the next lesson, we build the FastAPI application entry point — async-first with automatic OpenAPI documentation.
