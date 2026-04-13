---
layout: post
title: "Unit Tests for Business Logic"
description: "Test validators, transformers, and service layer in isolation with pytest"
categories: [python-production]
series: python-production
module: 5
module_order: 502
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-unit-tests
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Integration tests catch regressions but are slow and don't pinpoint the failure. Unit tests verify individual components in isolation — fast feedback, precise failure messages.

## Testing Pydantic Models

Pydantic models are pure validation logic — perfect for unit testing:

```python
import pytest
from pydantic import ValidationError
from app.api.models.items import ItemCreate


class TestItemCreate:
    def test_valid_item(self):
        item = ItemCreate(name="Widget", price=9.99)
        assert item.name == "Widget"
        assert item.price == 9.99
        assert item.description is None

    def test_with_description(self):
        item = ItemCreate(name="Widget", description="A fine widget", price=9.99)
        assert item.description == "A fine widget"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(name="", price=9.99)
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_negative_price_rejected(self):
        with pytest.raises(ValidationError):
            ItemCreate(name="Widget", price=-1)

    def test_zero_price_rejected(self):
        with pytest.raises(ValidationError):
            ItemCreate(name="Widget", price=0)

    def test_missing_name_rejected(self):
        with pytest.raises(ValidationError):
            ItemCreate(price=9.99)

    def test_missing_price_rejected(self):
        with pytest.raises(ValidationError):
            ItemCreate(name="Widget")
```

These tests:
- Run in milliseconds (no HTTP, no async)
- Test boundary conditions (empty, zero, negative, missing)
- Use `pytest.raises` to verify expected failures

## Testing model_dump()

```python
def test_model_dump(self):
    item = ItemCreate(name="Widget", description="Nice", price=9.99)
    data = item.model_dump()
    assert data == {"name": "Widget", "description": "Nice", "price": 9.99}

def test_model_dump_excludes_none(self):
    item = ItemCreate(name="Widget", price=9.99)
    data = item.model_dump(exclude_none=True)
    assert "description" not in data
```

## Testing Config

```python
import os

class TestSettings:
    def test_defaults(self):
        from app.config import Settings
        s = Settings()
        assert s.app_name == "python-production-blueprint"
        assert s.vault_enabled is False

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("APP_NAME", "test-app")
        monkeypatch.setenv("VAULT_ENABLED", "true")
        from app.config import Settings
        s = Settings()
        assert s.app_name == "test-app"
        assert s.vault_enabled is True

    def test_is_production(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "production")
        from app.config import Settings
        s = Settings()
        assert s.is_production is True
```

`monkeypatch` is a pytest fixture that temporarily sets environment variables — cleaned up automatically after each test.

## When to Unit Test vs Integration Test

| Test Type | What | Speed | Scope |
|-----------|------|-------|-------|
| Unit | Model validation, config, utilities | 1ms | One function |
| Integration | Full HTTP request → response | 50ms | Route + middleware + model |
| E2E | Docker → API → Database → Response | 1s+ | Full stack |

Unit tests run first in CI — fast failure. Integration tests follow.

## Next Step

In the next lesson, we write integration tests for API endpoints — testing full request-response cycles with the async test client.
