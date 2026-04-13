---
layout: post
title: "Request-Scoped Logging with Correlation IDs"
description: "Trace a request across log lines with middleware-injected correlation IDs using structlog contextvars"
categories: [python-production]
series: python-production
module: 3
module_order: 303
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-correlation-ids
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

A request triggers 5 log lines across your application — route handler, business logic, database call, external API, response. Without correlation, these 5 lines are lost among thousands of others. You need every log line from a single request to share a unique identifier.

## The Middleware

```python
# app/middleware/logging_middleware.py
import time
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        # Bind context for ALL downstream logs
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        logger = structlog.get_logger("http.request")

        await logger.ainfo(
            "request_started",
            query_params=str(request.query_params) if request.query_params else None,
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            await logger.aexception("request_failed", duration_ms=duration_ms)
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        await logger.ainfo(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        structlog.contextvars.clear_contextvars()
        return response
```

## How contextvars Works

`structlog.contextvars` uses Python's `contextvars` module to store data that's scoped to the current async task:

```python
# Middleware sets context
structlog.contextvars.bind_contextvars(
    request_id="abc-123",
    method="POST",
    path="/api/v1/items/",
)

# In the route handler (different function, same async context)
await logger.ainfo("item_created", item_id="xyz")
```

Output:
```json
{
  "event": "item_created",
  "item_id": "xyz",
  "request_id": "abc-123",
  "method": "POST",
  "path": "/api/v1/items/"
}
```

The route handler never passed `request_id` — it was injected by the middleware.

## Request Flow

```
Client → Middleware (bind context) → Route → Logger → Output
                                       ↓
                                   Business Logic → Logger → Output
                                       ↓
                                   Database Call → Logger → Output
         Middleware (log response, clear context) ←─────────┘
```

Every logger call within this request automatically includes `request_id`, `method`, `path`, and `client_ip`.

## X-Request-ID Header

```python
request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
```

If the client sends `X-Request-ID`, it's preserved. This enables distributed tracing across service boundaries — the API gateway generates the ID, and all downstream services use it.

```python
response.headers["X-Request-ID"] = request_id
```

The ID is returned in the response so the client can reference it in support tickets.

## Searching by Correlation ID

In Elasticsearch/Kibana:
```
request_id: "abc-123"
```

Returns every log line for that request, ordered by timestamp, from every service:

```json
{"event": "request_started", "request_id": "abc-123", "path": "/api/v1/items/"}
{"event": "item_created", "request_id": "abc-123", "item_id": "xyz"}
{"event": "request_completed", "request_id": "abc-123", "status_code": 201, "duration_ms": 12.5}
```

## Clean Context Lifecycle

```python
structlog.contextvars.clear_contextvars()   # Start clean
structlog.contextvars.bind_contextvars(...)  # Set context
# ... request processing ...
structlog.contextvars.clear_contextvars()   # Cleanup after response
```

Always clear at start AND end. Previous request context must not leak into the next request.

## Next Step

In the next lesson, we add dual output — stdout for containers and file-based logging for Marathon/host-mount deployments.
