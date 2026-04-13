---
layout: post
title: "FastAPI — Async-First HTTP Framework"
description: "Build your first async API with automatic OpenAPI docs, lifespan events, and structured application factory"
categories: [python-production]
series: python-production
module: 1
module_order: 102
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-fastapi-basics
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

You need an HTTP framework that's fast, has automatic API docs, supports async natively, and doesn't require a separate WSGI server. Flask needs Gunicorn, Django is heavy for microservices, and Tornado is low-level.

FastAPI gives you all of this with Python type hints — no decorators for validation, no manual schema writing.

## Application Factory Pattern

Don't create the app at module level. Use a factory function — it's testable, configurable, and avoids circular imports:

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.routing import Route

from app.api.routes.health import router as health_router
from app.api.routes.items import router as items_router
from app.config import settings
from app.logging_config import get_logger, setup_logging
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.telemetry.metrics import metrics_endpoint
from app.telemetry.tracing import setup_tracing
from app.vault import load_vault_secrets

# Initialize logging FIRST — before any logger is used
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load secrets, initialize connections
    vault_secrets = load_vault_secrets()
    app.state.vault_secrets = vault_secrets

    logger.info(
        "application_starting",
        app_name=settings.app_name,
        environment=settings.app_env,
        version=settings.app_version,
    )
    yield
    # Shutdown: close connections, flush buffers
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    # Middleware (order matters: first added = outermost)
    app.add_middleware(RequestLoggingMiddleware)

    # Routes
    app.include_router(health_router)
    app.include_router(items_router)

    # Prometheus metrics endpoint
    app.routes.append(Route("/metrics", metrics_endpoint))

    # OpenTelemetry tracing (if enabled)
    setup_tracing(app)

    return app


app = create_app()
```

## Key Concepts

### Lifespan Events

The `@asynccontextmanager` pattern replaces the deprecated `on_startup`/`on_shutdown` events:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Everything before `yield` runs at startup
    vault_secrets = load_vault_secrets()
    app.state.vault_secrets = vault_secrets
    
    yield  # App is running
    
    # Everything after `yield` runs at shutdown
    logger.info("application_shutting_down")
```

Use startup for: loading secrets, warming caches, establishing DB pools.
Use shutdown for: closing connections, flushing logs, sending final metrics.

### Conditional Docs

```python
docs_url="/docs" if not settings.is_production else None,
```

Swagger UI in development, disabled in production. Attackers use `/docs` to map your API surface.

### Middleware Order

```python
app.add_middleware(RequestLoggingMiddleware)
```

First middleware added = outermost wrapper. The logging middleware wraps every request, so it must be added first.

### Route Organization

```python
app.include_router(health_router)
app.include_router(items_router)
```

Each domain gets its own router in a separate file. Health routes have no prefix. Business routes use `/api/v1/` prefix.

## Running the App

```bash
# Development — with hot reload
docker compose up

# Direct (if you have dependencies installed)
uvicorn app.main:app --reload --log-level debug
```

The `docker compose up` approach is preferred — no virtualenv, no system-level pip installs.

## Verify It Works

```bash
# Health check
curl http://localhost:8000/health

# API docs (development only)
open http://localhost:8000/docs

# Create an item
curl -X POST http://localhost:8000/api/v1/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "price": 9.99}'
```

## Next Step

In the next lesson, we build the Pydantic models for request validation and response serialization.
