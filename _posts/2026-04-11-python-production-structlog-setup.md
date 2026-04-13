---
layout: post
title: "structlog — JSON Logging with Context"
description: "Configure structlog with processors, renderers, and context binding for production Python applications"
categories: [python-production]
series: python-production
module: 3
module_order: 302
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-structlog-setup
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Python's built-in `logging` module produces flat text strings. Adding context requires string formatting: `logger.info(f"Created item {item_id} for user {user_id}")`. This context is embedded in text — not queryable.

structlog produces structured key-value log events that are machine-parseable.

## The Full Configuration

```python
# app/logging_config.py
import logging
import sys
import structlog
from app.config import settings


def setup_logging() -> None:
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Shared processors — run on every log event
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Choose renderer based on environment
    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Formatter for stdout
    stdout_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_formatter)
    root_logger.addHandler(stdout_handler)
    root_logger.setLevel(log_level)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
```

## Processor Pipeline

Every log event flows through processors in order:

```
Log Event → merge_contextvars → filter_by_level → add_logger_name
         → add_log_level → TimeStamper → StackInfoRenderer
         → UnicodeDecoder → JSONRenderer → Output
```

| Processor | What It Does |
|-----------|-------------|
| `merge_contextvars` | Adds request-scoped context (request_id, method, path) |
| `filter_by_level` | Drops events below configured log level |
| `add_logger_name` | Adds `logger` field (module name) |
| `add_log_level` | Adds `level` field |
| `TimeStamper(fmt="iso")` | Adds ISO 8601 timestamp |
| `JSONRenderer` | Serializes everything to JSON |

## Using the Logger

```python
from app.logging_config import get_logger

logger = get_logger(__name__)

# Sync logging
logger.info("item_created", item_id="abc-123", name="Widget")

# Async logging (inside async functions)
await logger.ainfo("item_created", item_id="abc-123", name="Widget")
```

Output:
```json
{
  "timestamp": "2026-04-11T10:15:23.456789Z",
  "level": "info",
  "logger": "app.api.routes.items",
  "event": "item_created",
  "item_id": "abc-123",
  "name": "Widget"
}
```

## JSON vs Console Renderer

**JSON** (`LOG_FORMAT=json`) — for production:
```json
{"timestamp": "2026-04-11T10:15:23Z", "level": "info", "event": "item_created", "item_id": "abc-123"}
```

**Console** (`LOG_FORMAT=console`) — for development:
```
2026-04-11T10:15:23Z [info     ] item_created          item_id=abc-123
```

Same data, different rendering. Set via environment variable — no code change.

## stdlib Integration

structlog wraps Python's standard `logging` module. This means:
- Third-party libraries that use `logging` still work
- Log levels work the same (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- Handlers (stdout, file, syslog) are standard logging handlers

## Next Step

In the next lesson, we add request-scoped logging with correlation IDs — trace a single request across all log lines using middleware.
