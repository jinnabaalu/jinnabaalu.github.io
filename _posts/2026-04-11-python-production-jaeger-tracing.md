---
layout: post
title: "Jaeger — Visualizing Distributed Traces"
description: "Deploy Jaeger, send traces via OTLP, and diagnose latency bottlenecks with the Jaeger UI"
categories: [python-production]
series: python-production
module: 7
module_order: 703
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-jaeger-tracing
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

You have traces being generated. Now you need to see them. Jaeger is an open-source distributed tracing backend — it stores traces and provides a UI for searching and visualizing them.

## Running Jaeger

```yaml
# infrastructure/docker-compose.yml (relevant service)
services:
  jaeger:
    image: jaegertracing/all-in-one:1.53
    container_name: jaeger
    environment:
      COLLECTOR_OTLP_ENABLED: "true"
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC receiver
      - "4318:4318"    # OTLP HTTP receiver
```

The `all-in-one` image includes collector, query service, and UI — perfect for development and small-scale production.

## Connecting Your App

```bash
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
```

Your app sends traces via OTLP gRPC to port 4317. Jaeger stores them in memory (development) or a backing store like Elasticsearch or Cassandra (production).

## Using the Jaeger UI

Open `http://localhost:16686`:

1. **Service dropdown** — Select `python-production-blueprint`
2. **Operation dropdown** — Filter by endpoint (e.g., `POST /api/v1/items/`)
3. **Search** — Find traces by time range, duration, tags
4. **Trace detail** — Click a trace for the waterfall diagram

### Reading the Waterfall

```
POST /api/v1/items/  ████████████████████████  45ms
  validate_input     ██                         2ms
  DB INSERT          ██████████████████         30ms
  log_event          █                          1ms
```

The DB insert is the bottleneck — 67% of request time. Without tracing, you'd be guessing.

### Searching by Tags

| Query | Finds |
|-------|-------|
| `http.status_code=500` | All server errors |
| `http.method=POST` | All POST requests |
| `min_duration > 1s` | Slow requests |

## Jaeger for Multiple Services

If you have Service A calling Service B:

```
Service A: POST /api/v1/orders/
├── Span: validate_order (5ms)
├── Span: HTTP POST service-b/api/v1/inventory/ (120ms)  ← crosses service boundary
│   └── Service B: POST /api/v1/inventory/
│       ├── Span: check_stock (15ms)
│       └── Span: DB SELECT inventory (95ms)
└── Span: DB INSERT orders (25ms)
```

The `traceparent` header carries the trace context. Service B's spans appear as children of Service A's HTTP call span.

## Production Jaeger

For production, use a distributed backend:

```yaml
jaeger:
  image: jaegertracing/all-in-one:1.53
  environment:
    SPAN_STORAGE_TYPE: elasticsearch
    ES_SERVER_URLS: http://elasticsearch:9200
```

Or use Grafana Tempo as the backend — it's designed for high-volume trace storage.

## Next Step

In the next lesson, we add Prometheus metrics — the RED method for monitoring Rate, Errors, and Duration.
