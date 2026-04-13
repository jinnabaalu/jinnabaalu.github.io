---
layout: post
title: "Error Handling & Response Models"
description: "Consistent error responses, exception handlers, and HTTP status codes for production APIs"
categories: [python-production]
series: python-production
module: 1
module_order: 105
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-error-handling
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Without consistent error handling, your API returns different error shapes from different endpoints. One route returns `{"error": "not found"}`, another returns `{"message": "Not Found"}`, and Pydantic validation returns a completely different structure. Clients can't reliably parse errors.

## HTTPException — Structured Errors

FastAPI's `HTTPException` returns consistent error responses:

```python
from fastapi import HTTPException

@router.get("/{item_id}")
async def get_item(item_id: str) -> ItemResponse:
    item = _items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

Response:
```json
{
  "detail": "Item not found"
}
```

## Validation Errors (422)

Pydantic validation failures return **422 Unprocessable Entity** automatically:

```bash
curl -X POST /api/v1/items/ -d '{"name": "", "price": -1}'
```

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": ""
    },
    {
      "type": "greater_than",
      "loc": ["body", "price"],
      "msg": "Input should be greater than 0",
      "input": -1
    }
  ]
}
```

Each error includes:
- `loc` — where the error occurred (body, query, path)
- `msg` — human-readable message
- `type` — machine-readable error type
- `input` — the invalid value

## Custom Exception Handlers

For application-specific errors, create custom exceptions:

```python
# app/api/exceptions.py
class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} '{identifier}' not found",
            status_code=404,
        )
```

Register the handler in your app factory:

```python
from fastapi.responses import JSONResponse

@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
```

## HTTP Status Code Conventions

| Status | When to Use |
|--------|-------------|
| **200** | Successful GET, PUT, PATCH |
| **201** | Successful POST (resource created) |
| **204** | Successful DELETE (no content) |
| **400** | Bad request (malformed JSON, business rule violation) |
| **404** | Resource not found |
| **409** | Conflict (duplicate, optimistic locking failure) |
| **422** | Validation error (Pydantic handles this) |
| **500** | Unhandled server error |

## Logging Errors

Every error path should log — with context:

```python
if not item:
    await logger.awarning("item_not_found", item_id=item_id)
    raise HTTPException(status_code=404, detail="Item not found")
```

`awarning` (not `ainfo`) — 404s are warnings, not normal operations. They help you detect broken client integrations.

## Next Step

In the next lesson, we add async database operations — SQLAlchemy async sessions and connection pooling.
