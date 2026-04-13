---
layout: post
title: "pytest — Fixtures, Conftest, and Async Testing"
description: "Set up pytest with fixtures, conftest.py, and async test support for FastAPI applications"
categories: [python-production]
series: python-production
module: 5
module_order: 501
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-pytest-setup
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Testing async FastAPI apps needs async test support, a test client that speaks ASGI, and shared fixtures across test files. Standard `unittest` doesn't support any of this natively.

## Test Setup

### conftest.py — Shared Fixtures

```python
# tests/conftest.py
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

This fixture:
- Creates an `AsyncClient` that talks directly to your FastAPI app (no HTTP server needed)
- Uses `ASGITransport` — in-process, no network overhead
- `yield` makes it a generator fixture — cleanup happens after the test
- Available to all test files (conftest.py is auto-discovered by pytest)

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --tb=short --cov=app --cov-report=term-missing"
```

- `asyncio_mode = "auto"` — async test functions run automatically, no `@pytest.mark.asyncio` needed
- `--cov=app` — measure coverage for the `app/` package
- `--cov-report=term-missing` — show which lines aren't covered

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test class
pytest tests/test_api.py::TestItemsAPI

# Run a specific test
pytest tests/test_api.py::TestItemsAPI::test_create_item
```

## Why httpx Over TestClient

FastAPI provides `TestClient` (based on `requests`), but it's synchronous. For async code:

| Feature | TestClient (requests) | AsyncClient (httpx) |
|---------|----------------------|---------------------|
| Async support | ❌ Wraps in sync | ✅ Native async |
| Event loop | Creates its own | Uses test's event loop |
| In-process | ✅ | ✅ |
| API compatible | requests-like | requests-like |

`httpx.AsyncClient` with `ASGITransport` is the modern approach for testing async FastAPI apps.

## Fixture Scope

The `client` fixture has default scope (`function`) — a new client per test. This ensures tests are isolated. For expensive setup (database connections), use broader scopes:

```python
@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()
```

## Next Step

In the next lesson, we write unit tests for business logic — testing validators and service functions in isolation.
