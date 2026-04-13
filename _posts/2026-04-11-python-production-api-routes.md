---
layout: post
title: "RESTful Route Design with FastAPI Router"
description: "Organize routes with APIRouter, path parameters, query parameters, and dependency injection"
categories: [python-production]
series: python-production
module: 1
module_order: 104
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-api-routes
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

All routes in one file becomes unmanageable at 10+ endpoints. You also need consistent URL patterns, proper HTTP methods, and a way to share dependencies (auth, DB sessions) across routes.

## APIRouter — Modular Route Organization

```python
# app/api/routes/items.py
import uuid
from fastapi import APIRouter, HTTPException
from app.api.models.items import ItemCreate, ItemListResponse, ItemResponse
from app.logging_config import get_logger

router = APIRouter(prefix="/api/v1/items", tags=["items"])
logger = get_logger(__name__)

# In-memory store (replace with a real DB)
_items: dict[str, ItemResponse] = {}
```

### `prefix="/api/v1/items"` — URL Namespace

All routes in this router start with `/api/v1/items`. The route decorator only specifies the sub-path:

```python
@router.post("/")       # → POST /api/v1/items/
@router.get("/")        # → GET  /api/v1/items/
@router.get("/{item_id}")  # → GET  /api/v1/items/{item_id}
```

### `tags=["items"]` — OpenAPI Grouping

Routes are grouped under "items" in Swagger UI. Makes large APIs navigable.

## CRUD Implementation

### Create (POST)

```python
@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate) -> ItemResponse:
    item_id = str(uuid.uuid4())
    created = ItemResponse(id=item_id, **item.model_dump())
    _items[item_id] = created
    await logger.ainfo("item_created", item_id=item_id, name=item.name)
    return created
```

- `status_code=201` — HTTP 201 Created, not the default 200
- `response_model=ItemResponse` — Response schema for OpenAPI docs

### List (GET)

```python
@router.get("/", response_model=ItemListResponse)
async def list_items() -> ItemListResponse:
    items = list(_items.values())
    await logger.ainfo("items_listed", count=len(items))
    return ItemListResponse(items=items, total=len(items))
```

Returns a wrapper with `items` array and `total` count — pagination-ready.

### Get by ID (GET)

```python
@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str) -> ItemResponse:
    item = _items.get(item_id)
    if not item:
        await logger.awarning("item_not_found", item_id=item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

- Path parameter `{item_id}` is extracted and typed automatically
- `HTTPException(status_code=404)` returns proper HTTP error responses

### Delete (DELETE)

```python
@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    if item_id not in _items:
        await logger.awarning("item_not_found", item_id=item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
    await logger.ainfo("item_deleted", item_id=item_id)
```

- `status_code=204` — No Content, standard for successful deletes
- Return type `None` — no response body

## Health Routes — A Separate Router

```python
# app/api/routes/health.py
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }

@router.get("/ready")
async def readiness_check() -> dict:
    return {"status": "ready"}
```

No prefix — health and readiness at root level: `/health` and `/ready`.

## Registering Routers

```python
# app/main.py
app.include_router(health_router)
app.include_router(items_router)
```

Each router is a separate module. Add new domains by creating a new file and calling `include_router()`.

## REST Conventions Used

| Operation | Method | Path | Status |
|-----------|--------|------|--------|
| Create | POST | `/api/v1/items/` | 201 |
| List | GET | `/api/v1/items/` | 200 |
| Get one | GET | `/api/v1/items/{id}` | 200 |
| Delete | DELETE | `/api/v1/items/{id}` | 204 |
| Not found | — | — | 404 |
| Validation error | — | — | 422 |

## Next Step

In the next lesson, we build consistent error handling — exception handlers, structured error responses, and HTTP status code conventions.
