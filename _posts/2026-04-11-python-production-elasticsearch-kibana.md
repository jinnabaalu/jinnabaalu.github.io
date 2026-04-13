---
layout: post
title: "Elasticsearch + Kibana — Search and Visualize"
description: "Index logs in Elasticsearch, build Kibana dashboards for production log analysis"
categories: [python-production]
series: python-production
module: 8
module_order: 804
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-elasticsearch-kibana
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Logs are in Kafka, processed by Vector, and ready for storage. You need a search engine that can handle millions of JSON documents and let you query across any field in milliseconds.

## Elasticsearch — The Log Store

```yaml
# infrastructure/docker-compose.elasticsearch.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    ports:
      - "9200:9200"
    volumes:
      - es-data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## Daily Index Pattern

Vector writes to `app-logs-2026-04-11`. Each day gets a new index. Benefits:

- **Retention:** Delete `app-logs-2026-03-*` to remove March logs
- **Performance:** Smaller indices = faster queries
- **ILM:** Age-based policies (hot → warm → cold → delete)

## Searching Logs in Kibana

Open `http://localhost:5601`

### Create Data View

1. Stack Management → Data Views → Create
2. Index pattern: `app-logs-*`
3. Time field: `timestamp`

### Key Queries

```
# Find all errors
level: "error"

# Find a specific request
request_id: "abc-123"

# Find slow requests
duration_ms > 1000

# Find by endpoint
path: "/api/v1/items/" AND method: "POST"

# Find by status code
status_code: 500

# Combine
level: "error" AND path: "/api/v1/items/" AND duration_ms > 500
```

### Build a Dashboard

Create panels for:
- **Request rate** — count of events over time
- **Error rate** — count where `level: "error"` over time
- **Top endpoints** — terms aggregation on `path`
- **Slow requests** — filter `duration_ms > 1000`, table with details
- **Status code distribution** — pie chart of `status_code`

## Index Lifecycle Management (ILM)

For production, configure retention:

```json
PUT _ilm/policy/app-logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "10gb",
            "max_age": "1d"
          }
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

Logs older than 30 days are automatically deleted.

## What You Can See Now

With the full pipeline running:

1. **Real-time logs** — events appear in Kibana within seconds
2. **Search any field** — `request_id`, `item_id`, `client_ip`, `duration_ms`
3. **Correlate** — find all logs for a request across all services
4. **Alert** — set up Kibana alerts for error spikes
5. **Dashboard** — real-time request rate, error rate, latency

## Next Step

In the next lesson, we wire everything together — the complete end-to-end pipeline from application to Kibana dashboard.
