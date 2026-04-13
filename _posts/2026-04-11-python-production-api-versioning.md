---
layout: post
title: "API Versioning Strategies"
description: "URL-based, header-based versioning and backward compatibility patterns for production APIs"
categories: [python-production]
series: python-production
module: 2
module_order: 204
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-api-versioning
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

You deployed v1 of your API. Now clients depend on it. You need to change the response format, add required fields, or restructure endpoints. Without versioning, every change risks breaking existing clients.

## Strategy 1: URL-Based Versioning (Recommended)

This is what our blueprint uses:

```python
router = APIRouter(prefix="/api/v1/items", tags=["items"])
```

When you need v2:

```python
# app/api/routes/items_v2.py
router_v2 = APIRouter(prefix="/api/v2/items", tags=["items-v2"])
```

Register both:

```python
app.include_router(items_router)     # /api/v1/items
app.include_router(items_v2_router)  # /api/v2/items
```

**Pros:** Explicit, cacheable, easy to test, visible in access logs.
**Cons:** URL changes between versions.

## Strategy 2: Header-Based Versioning

```python
from fastapi import Header

@router.get("/items/")
async def list_items(accept_version: str = Header("v1", alias="Accept-Version")):
    if accept_version == "v2":
        return v2_response()
    return v1_response()
```

Client sends:
```
GET /api/items/
Accept-Version: v2
```

**Pros:** Clean URLs, single endpoint.
**Cons:** Hard to test in browser, invisible in logs.

## When to Version

| Change Type | Need Version? |
|-------------|---------------|
| Add optional field to response | No |
| Add new endpoint | No |
| Remove field from response | **Yes** |
| Change field type | **Yes** |
| Rename field | **Yes** |
| Change status codes | **Yes** |
| Add required field to request | **Yes** |

### Non-Breaking Changes (No Version Needed)

- Adding optional response fields
- Adding new endpoints
- Adding optional query parameters
- Fixing bugs

### Breaking Changes (New Version)

- Removing or renaming fields
- Changing data types
- Restructuring response format
- Adding required request fields

## Version Sunset Strategy

```python
import warnings
from datetime import date

@router_v1.get("/items/")
async def list_items_v1():
    """Deprecated: Use /api/v2/items/ instead. Sunset: 2026-06-01"""
    response = await _get_items()
    return JSONResponse(
        content=response,
        headers={
            "Sunset": "Sat, 01 Jun 2026 00:00:00 GMT",
            "Deprecation": "true",
            "Link": '</api/v2/items/>; rel="successor-version"',
        },
    )
```

HTTP `Sunset` header tells clients when the version will be removed.

## Our Blueprint's Approach

We use **URL-based versioning** with `/api/v1/` prefix:

```
/health          ← No version (infrastructure)
/ready           ← No version (infrastructure)
/metrics         ← No version (infrastructure)
/api/v1/items/   ← Versioned business API
```

Health, readiness, and metrics endpoints are **not versioned** — they're infrastructure contracts, not business APIs.

## Next Step

Module 2 complete. In Module 3, we tackle configuration and secrets — pydantic-settings for type-safe config, and HashiCorp Vault for production secrets.
