---
layout: post
title: "Vector Aggregator — Transform and Route"
description: "Parse, enrich, and route logs from Kafka to storage backends with Vector Aggregator"
categories: [python-production]
series: python-production
module: 8
module_order: 803
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-vector-aggregator
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Raw logs from Kafka need enrichment before indexing. You may want to add metadata, filter noisy events, route errors to a separate index, or transform fields. The aggregator handles this centrally — changes apply to all logs without touching individual agents.

## Vector Aggregator Configuration

```toml
# infrastructure/vector/vector-aggregator.toml

# SOURCES: Read from Kafka topic
[sources.kafka]
type = "kafka"
bootstrap_servers = "kafka:9092"
topics = ["app-logs"]
group_id = "vector-aggregator"
decoding.codec = "json"

# TRANSFORMS: Enrich before indexing
[transforms.enrich]
type = "remap"
inputs = ["kafka"]
source = '''
if !exists(.timestamp) {
  .timestamp = now()
}
.aggregator_processed_at = now()
.pipeline = "kafka-to-elasticsearch"
'''

# SINKS: Ship to Elasticsearch
[sinks.elasticsearch]
type = "elasticsearch"
inputs = ["enrich"]
endpoints = ["http://elasticsearch:9200"]
bulk.index = "app-logs-%Y-%m-%d"
encoding.except_fields = ["source_type"]

[sinks.elasticsearch.buffer]
type = "disk"
max_size = 268435456  # 256MB
when_full = "block"
```

## Architecture Role

```
Vector Agent → Kafka → [Vector Aggregator] → Elasticsearch
                              ↓
                        Enrich, transform,
                        filter, route
```

The aggregator is the **central processing point**. Agents are lightweight collectors. The aggregator does the heavy lifting.

## Transform: Enrichment

```toml
source = '''
if !exists(.timestamp) {
  .timestamp = now()
}
.aggregator_processed_at = now()
.pipeline = "kafka-to-elasticsearch"
'''
```

- Ensures every event has a timestamp
- Adds processing metadata for debugging the pipeline itself

## Elasticsearch Sink

### Daily Indices

```toml
bulk.index = "app-logs-%Y-%m-%d"
```

Creates indices like `app-logs-2026-04-11`. Daily indices enable:
- Easy retention (delete old indices)
- Smaller index sizes for faster queries
- ILM (Index Lifecycle Management) policies

### Disk Buffer

```toml
[sinks.elasticsearch.buffer]
type = "disk"
max_size = 268435456
when_full = "block"
```

If Elasticsearch is slow or temporarily down, Vector buffers to disk. No logs lost.

## Advanced Transforms

### Filter Noisy Events

```toml
[transforms.filter_health]
type = "filter"
inputs = ["enrich"]
condition = '.path != "/health" && .path != "/ready" && .path != "/metrics"'
```

Health check logs are noise — filter them out before indexing.

### Route Errors to Separate Index

```toml
[transforms.route_by_level]
type = "route"
inputs = ["enrich"]
route.errors = '.level == "error" || .level == "critical"'
route._unmatched = true

[sinks.es_errors]
type = "elasticsearch"
inputs = ["route_by_level.errors"]
endpoints = ["http://elasticsearch:9200"]
bulk.index = "app-errors-%Y-%m-%d"

[sinks.es_all]
type = "elasticsearch"
inputs = ["route_by_level._unmatched"]
endpoints = ["http://elasticsearch:9200"]
bulk.index = "app-logs-%Y-%m-%d"
```

Errors go to `app-errors-*` (fast to search, separate alerts). Normal logs go to `app-logs-*`.

## Running the Aggregator

```yaml
# infrastructure/docker-compose.vector.yml
services:
  vector-aggregator:
    image: timberio/vector:0.35.0-alpine
    container_name: vector-aggregator
    volumes:
      - ./vector/vector-aggregator.toml:/etc/vector/vector.toml:ro
      - vector-agg-data:/var/lib/vector
    depends_on:
      - kafka
```

## Next Step

In the next lesson, we set up Elasticsearch and Kibana — the storage and visualization layer for our log pipeline.
