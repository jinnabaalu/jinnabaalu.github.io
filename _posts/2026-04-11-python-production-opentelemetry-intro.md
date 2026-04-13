---
layout: post
title: "OpenTelemetry — Traces, Spans, and Context"
description: "Understand distributed traces, spans, and how context propagates across services with OpenTelemetry"
categories: [python-production]
series: python-production
module: 7
module_order: 701
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-opentelemetry-intro
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

A request takes 3 seconds. Is it the database? The external API? The serialization layer? With logs alone, you can see timestamps but not the hierarchy of calls. You need to see the **call tree** — which function called which, and how long each took.

## Concepts

### Trace

A trace represents a single request's journey through your system. It has a unique `trace_id`.

### Span

A span is one operation within a trace — an HTTP request, a database query, an external API call. Spans have:
- Start time and duration
- Parent span (creating a tree)
- Attributes (key-value metadata)
- Status (OK, ERROR)

### Context Propagation

When Service A calls Service B, the `trace_id` is passed via HTTP headers (`traceparent`). Service B's spans join the same trace.

```
Trace: abc-123
├── Span: POST /api/v1/items/ (45ms)
│   ├── Span: validate_input (2ms)
│   ├── Span: DB INSERT items (30ms)
│   └── Span: log_event (1ms)
```

## OpenTelemetry — The Standard

OpenTelemetry (OTel) is the CNCF standard for observability. It provides:
- **API** — Interfaces for creating traces, metrics, logs
- **SDK** — Reference implementation
- **Exporters** — Send data to backends (Jaeger, Tempo, Datadog)
- **Auto-instrumentation** — Framework-specific plugins

## Our Implementation

```python
# app/telemetry/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def setup_tracing(app) -> None:
    if not settings.otel_enabled:
        logger.info("opentelemetry_disabled")
        return

    resource = Resource.create({
        "service.name": settings.otel_service_name,
        "service.version": settings.app_version,
        "deployment.environment": settings.app_env,
    })

    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        insecure=True,
    )
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(provider)

    # Auto-instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Inject trace_id into log records
    LoggingInstrumentor().instrument(set_logging_format=True)

    logger.info(
        "opentelemetry_initialized",
        endpoint=settings.otel_exporter_otlp_endpoint,
    )
```

## Key Components

### Resource — Service Identity

```python
Resource.create({
    "service.name": "python-production-blueprint",
    "service.version": "0.2.0",
    "deployment.environment": "staging",
})
```

Every span carries this metadata. In Jaeger, you search by service name.

### OTLP Exporter — Send Traces

```python
OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
```

OTLP (OpenTelemetry Protocol) over gRPC. Jaeger, Tempo, and most backends accept OTLP natively.

### BatchSpanProcessor — Efficient Export

```python
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
```

Batches spans before export — doesn't send one-by-one. Reduces overhead on your application.

### LoggingInstrumentor — Bridge Logs and Traces

```python
LoggingInstrumentor().instrument(set_logging_format=True)
```

Injects `trace_id` and `span_id` into Python log records. Your structured logs now link directly to traces.

## Configuration

```bash
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
OTEL_SERVICE_NAME=python-production-blueprint
```

Set `OTEL_ENABLED=false` to disable tracing entirely — zero overhead.

## Next Step

In the next lesson, we dive into auto-instrumentation — how FastAPI traces every request without any code changes.
