---
layout: post
title: "Integration Tests for API Endpoints"
description: "Test full HTTP request-response cycles using httpx AsyncClient against your FastAPI app"
categories: [python-production]
series: python-production
module: 5
module_order: 503
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-integration-tests
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Unit tests verify individual components, but don't catch issues in how components interact — routing, middleware, serialization, error handling. Integration tests exercise the full stack inside the process.

## Test Client Setup

The `conftest.py` creates an async HTTP client that talks directly to the ASGI app — no real server needed:

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

Key points:
- `ASGITransport` bypasses the network — calls go straight to FastAPI's ASGI interface
- `base_url="http://test"` is a fake URL — no real HTTP server starts
- The `async with` ensures proper cleanup after each test

## Testing Health Endpoints

```python
class TestHealthEndpoints:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    async def test_readiness_check(self, client: AsyncClient):
        response = await client.get("/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
```

These test the health routes we built in Module 1 — verifying the response structure, not just the status code.

## Testing CRUD Operations

```python
class TestItemsAPI:
    async def test_create_item(self, client: AsyncClient):
        payload = {"name": "Test Item", "description": "A test item", "price": 9.99}
        response = await client.post("/api/v1/items/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["price"] == 9.99
        assert "id" in data

    async def test_list_items(self, client: AsyncClient):
        response = await client.get("/api/v1/items/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_item(self, client: AsyncClient):
        # Create first
        payload = {"name": "Fetch Me", "price": 5.0}
        create_resp = await client.post("/api/v1/items/", json=payload)
        item_id = create_resp.json()["id"]

        # Get
        response = await client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Fetch Me"

    async def test_get_item_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/items/nonexistent-id")
        assert response.status_code == 404
```

Pattern: **create → use → verify**. Each test creates its own data, avoiding test coupling.

## Testing Delete Lifecycle

```python
    async def test_delete_item(self, client: AsyncClient):
        # Create
        payload = {"name": "Delete Me", "price": 1.0}
        create_resp = await client.post("/api/v1/items/", json=payload)
        item_id = create_resp.json()["id"]

        # Delete
        response = await client.delete(f"/api/v1/items/{item_id}")
        assert response.status_code == 204

        # Verify deleted
        response = await client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 404

    async def test_delete_item_not_found(self, client: AsyncClient):
        response = await client.delete("/api/v1/items/nonexistent-id")
        assert response.status_code == 404
```

## Testing Validation Errors

```python
    async def test_create_item_validation_error(self, client: AsyncClient):
        # Missing required fields
        response = await client.post("/api/v1/items/", json={})
        assert response.status_code == 422

        # Invalid price
        response = await client.post(
            "/api/v1/items/", json={"name": "Bad", "price": -1}
        )
        assert response.status_code == 422
```

FastAPI returns 422 for Pydantic validation failures — test that clients get clear error responses.

## Testing Middleware

```python
class TestRequestLogging:
    async def test_request_id_header_returned(self, client: AsyncClient):
        response = await client.get("/health")
        assert "X-Request-ID" in response.headers

    async def test_custom_request_id_preserved(self, client: AsyncClient):
        custom_id = "test-request-123"
        response = await client.get(
            "/health", headers={"X-Request-ID": custom_id}
        )
        assert response.headers["X-Request-ID"] == custom_id
```

These test the `RequestLoggingMiddleware` we built in Module 4 — verifying correlation IDs flow through.

## Testing Metrics Endpoint

```python
class TestMetrics:
    async def test_prometheus_metrics_endpoint(self, client: AsyncClient):
        response = await client.get("/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text or "python" in response.text.lower()
```

## Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run a specific test class
pytest tests/test_api.py::TestItemsAPI

# Run a single test
pytest tests/test_api.py::TestItemsAPI::test_create_item -v
```

## Next Step

In the next lesson, we add test coverage measurement — ensuring our test suite actually exercises the code paths that matter.
