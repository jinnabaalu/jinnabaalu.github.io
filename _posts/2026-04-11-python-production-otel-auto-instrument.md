---
layout: post
title: "Auto-Instrumentation for FastAPI"
description: "Zero-code tracing for HTTP requests, database calls, and external API calls with OpenTelemetry"
categories: [python-production]
series: python-production
module: 7
module_order: 702
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-otel-auto-instrument
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Manually wrapping every function in spans is tedious and error-prone. You'd need to modify every route handler, database call, and HTTP client. Auto-instrumentation does this for you.

## What Auto-Instrumentation Traces

### FastAPI Instrumentation

```python
FastAPIInstrumentor.instrument_app(app)
```

This single line traces:
- Every incoming HTTP request (method, path, status code, duration)
- Route matching
- Exception propagation

Each request becomes a root span with attributes:

| Attribute | Example |
|-----------|---------|
| `http.method` | `POST` |
| `http.target` | `/api/v1/items/` |
| `http.status_code` | `201` |
| `http.route` | `/api/v1/items/` |

### HTTP Client Instrumentation

When your app calls external services using `httpx`:

```bash
pip install opentelemetry-instrumentation-httpx
```

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
HTTPXClientInstrumentor().instrument()
```

Now every `httpx.get()` or `httpx.post()` creates a child span with the outgoing request details and propagates the `traceparent` header.

### Database Instrumentation

```bash
pip install opentelemetry-instrumentation-sqlalchemy
# or
pip install opentelemetry-instrumentation-pymongo
```

```python
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
SQLAlchemyInstrumentor().instrument(engine=engine)
```

Every SQL query becomes a span with the query text and duration.

## What a Trace Looks Like

```
Trace: 4bf92f3577b34da6a3ce929d0e0e4736
│
├─ POST /api/v1/items/ [45ms]
│  ├─ validate_request [2ms]
│  ├─ INSERT INTO items... [28ms]  ← DB instrumentation
│  ├─ POST https://webhook.site/notify [12ms]  ← HTTP client
│  └─ serialize_response [1ms]
```

In Jaeger UI, this renders as a waterfall diagram — immediately showing that the DB insert takes 62% of total time.

## Logging Integration

```python
LoggingInstrumentor().instrument(set_logging_format=True)
```

After this, every log record includes `otelTraceID` and `otelSpanID`:

```json
{
  "event": "item_created",
  "request_id": "abc-123",
  "otelTraceID": "4bf92f3577b34da6a3ce929d0e0e4736",
  "otelSpanID": "00f067aa0ba902b7"
}
```

Click the trace ID in Kibana → opens the trace in Jaeger. Logs and traces are linked.

## Dependencies

```toml
# pyproject.toml
dependencies = [
    "opentelemetry-api>=1.29.0",
    "opentelemetry-sdk>=1.29.0",
    "opentelemetry-instrumentation-fastapi>=0.50b0",
    "opentelemetry-instrumentation-logging>=0.50b0",
    "opentelemetry-exporter-otlp>=1.29.0",
]
```

## Zero-Code Alternative

OpenTelemetry also supports fully automatic instrumentation via the `opentelemetry-instrument` wrapper:

```bash
opentelemetry-instrument uvicorn app.main:app
```

This instruments everything without any code changes — but gives less control. Our approach (programmatic instrumentation) lets us control exactly what's traced and configure resources.

## Next Step

In the next lesson, we deploy Jaeger and visualize our traces — finding latency bottlenecks in real time.
