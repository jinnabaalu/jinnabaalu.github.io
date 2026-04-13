---
layout: post
title: "Pydantic — Request & Response Validation"
description: "Type-safe data models that validate at runtime with Pydantic v2 — request bodies, response schemas, and field constraints"
categories: [python-production]
series: python-production
module: 1
module_order: 103
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-pydantic-validation
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

APIs without validation accept anything — empty strings, negative prices, SQL injection payloads. Manual validation (`if not name: raise ...`) is tedious, inconsistent, and easy to forget.

Pydantic models validate automatically at the boundary. Invalid data never reaches your business logic.

## Define Models

```python
# app/api/models/items.py
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    price: float = Field(..., gt=0)


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str | None
    price: float


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
```

## What Each Part Does

### `Field(...)` — Required with Constraints

```python
name: str = Field(..., min_length=1, max_length=255)
```

- `...` (Ellipsis) means **required** — no default value
- `min_length=1` — empty strings rejected
- `max_length=255` — prevents oversized inputs

### `Field(None)` — Optional

```python
description: str | None = Field(None, max_length=1000)
```

- Defaults to `None` if not provided
- If provided, still validated against `max_length`

### `gt=0` — Numeric Constraints

```python
price: float = Field(..., gt=0)
```

- `gt` = greater than (exclusive)
- Also available: `ge` (>=), `lt` (<), `le` (<=)

## How FastAPI Uses Models

### Request Model (Input)

```python
@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate) -> ItemResponse:
    # 'item' is already validated — Pydantic parsed the JSON body
    item_id = str(uuid.uuid4())
    created = ItemResponse(id=item_id, **item.model_dump())
    return created
```

FastAPI sees the `item: ItemCreate` type hint and:
1. Reads the JSON request body
2. Validates it against `ItemCreate`
3. Returns **422 Unprocessable Entity** if validation fails
4. Passes the validated model to your function

### Response Model (Output)

```python
@router.get("/", response_model=ItemListResponse)
async def list_items() -> ItemListResponse:
    items = list(_items.values())
    return ItemListResponse(items=items, total=len(items))
```

`response_model=ItemListResponse` ensures the response matches the schema — extra fields are stripped.

## Validation in Action

```bash
# Valid request
curl -X POST /api/v1/items/ -d '{"name": "Widget", "price": 9.99}'
# → 201 Created

# Empty name
curl -X POST /api/v1/items/ -d '{"name": "", "price": 9.99}'
# → 422 {"detail": [{"loc": ["body", "name"], "msg": "String should have at least 1 character"}]}

# Negative price
curl -X POST /api/v1/items/ -d '{"name": "Widget", "price": -5}'
# → 422 {"detail": [{"loc": ["body", "price"], "msg": "Input should be greater than 0"}]}

# Missing required field
curl -X POST /api/v1/items/ -d '{}'
# → 422 (lists all missing fields)
```

## model_dump() — The Bridge

```python
created = ItemResponse(id=item_id, **item.model_dump())
```

`model_dump()` converts the Pydantic model to a plain dict. The `**` spread operator passes each key as a keyword argument. This is the Pydantic v2 replacement for v1's `.dict()`.

## Automatic OpenAPI Schema

FastAPI generates OpenAPI schemas from your Pydantic models — these appear in the Swagger UI at `/docs`. No separate schema files needed.

## Next Step

In the next lesson, we containerize the application with Docker — multi-stage build, non-root user, and a docker-compose dev workflow that eliminates the need for virtual environments.
