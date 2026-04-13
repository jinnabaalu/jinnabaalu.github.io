---
layout: post
title: "Prometheus Metrics — RED Method"
description: "Instrument your API with Prometheus client — Rate, Errors, Duration metrics for production monitoring"
categories: [python-production]
series: python-production
module: 7
module_order: 704
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-prometheus-metrics
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Tracing tells you what happened to one request. Metrics tell you what's happening to all requests. You need to answer: "How many requests per second? What's the error rate? What's the 99th percentile latency?"

## The RED Method

| Metric | Question | Type |
|--------|----------|------|
| **R**ate | How many requests/second? | Counter |
| **E**rrors | How many are failing? | Counter (by status code) |
| **D**uration | How long do they take? | Histogram |

## Implementation

```python
# app/telemetry/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)


def record_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code),
    ).inc()
    REQUEST_DURATION.labels(
        method=method,
        endpoint=endpoint,
    ).observe(duration)


async def metrics_endpoint(_request: Request) -> Response:
    return Response(
        content=generate_latest(),
        media_type="text/plain; charset=utf-8",
    )
```

## Metric Types

### Counter — Only Goes Up

```python
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)
```

Counts total requests. Prometheus calculates **rate** from counter values:

```promql
rate(http_requests_total[5m])  # Requests per second over 5 minutes
```

### Histogram — Distribution of Values

```python
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)
```

Records request durations in pre-defined buckets. Enables percentile queries:

```promql
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
# 99th percentile latency
```

## The /metrics Endpoint

```python
# app/main.py
from starlette.routing import Route
app.routes.append(Route("/metrics", metrics_endpoint))
```

Prometheus scrapes this endpoint every 15-30 seconds:

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status_code="200"} 1523.0
http_requests_total{method="POST",endpoint="/api/v1/items/",status_code="201"} 89.0
http_requests_total{method="POST",endpoint="/api/v1/items/",status_code="422"} 12.0

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.005"} 1500.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.01"} 1523.0
```

## Labels — Dimensions of Your Metrics

```python
["method", "endpoint", "status_code"]
```

Labels let you slice data:
- Error rate: `rate(http_requests_total{status_code=~"5.."}[5m])`
- Slow endpoints: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{endpoint="/api/v1/items/"}[5m]))`

**Warning:** High-cardinality labels (user IDs, request IDs) will overwhelm Prometheus. Use labels for bounded sets only (methods, endpoints, status codes).

## Custom Histogram Buckets

```python
buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
```

Default Prometheus buckets go up to 10 seconds. Adjust based on your SLOs. If your API should respond in under 100ms, add more fine-grained buckets below 0.1.

## Grafana Dashboards

Prometheus stores the data. Grafana visualizes it:

```promql
# Request rate panel
rate(http_requests_total[5m])

# Error rate panel
sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# p99 latency panel
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

## Next Step

Module 5 complete. In Module 6, we build the log pipeline — Vector Agent collects logs from files, Kafka buffers them, Vector Aggregator ships to Elasticsearch, and Kibana visualizes.
