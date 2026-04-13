---
layout: post
title: "End-to-End Pipeline"
description: "Wire it all together: App → File → Vector → Kafka → Elasticsearch → Kibana"
categories: [python-production]
series: python-production
module: 8
module_order: 805
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-log-pipeline-e2e
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Complete Pipeline

```
┌─────────┐    ┌───────────┐    ┌───────┐    ┌────────────┐    ┌──────┐    ┌────────┐
│ FastAPI  │───→│ Log Files │───→│Vector │───→│   Kafka    │───→│Vector│───→│   ES   │
│   App   │    │/var/log/  │    │Agent  │    │            │    │Aggr. │    │+Kibana │
└─────────┘    └───────────┘    └───────┘    └────────────┘    └──────┘    └────────┘
  structlog     RotatingFile     file→kafka    Durable buffer   kafka→es    Search+UI
```

## Starting the Full Stack

```bash
# From the project root
cd infrastructure
docker compose up -d
```

This starts: Elasticsearch, Kibana, Kafka, Vector Agent, Vector Aggregator, Jaeger, and the application.

## Verifying Each Stage

### 1. Application Logs to File

```bash
# Generate some traffic
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Widget", "price": 29.99}'

# Check log file
docker exec python-app cat /var/log/app/app.log
```

You should see JSON log lines with `request_id`, `method`, `path`, `duration_ms`.

### 2. Vector Agent Reads Files

```bash
# Check Vector Agent metrics
curl http://localhost:8686/health  # Vector API
```

Vector Agent tails `/var/log/app/*.log` and sends parsed events to Kafka.

### 3. Kafka Receives Events

```bash
# Check Kafka topic
docker exec kafka kafka-console-consumer.sh \
  --topic app-logs \
  --bootstrap-server localhost:9092 \
  --from-beginning \
  --max-messages 5
```

### 4. Vector Aggregator Ships to ES

Check `http://localhost:9200/app-logs-*/_count` — should show increasing document count.

### 5. Kibana Dashboard

Open `http://localhost:5601`:
1. Create data view for `app-logs-*`
2. Go to Discover tab
3. You should see your log events

## Docker Compose — The Full Infrastructure

```yaml
# infrastructure/docker-compose.yml
include:
  - docker-compose.elasticsearch.yml
  - docker-compose.kafka.yml
  - docker-compose.vector.yml
  - docker-compose.vault.yml
  - docker-compose.app.yml
```

Each component has its own compose file — modular, testable, independently deployable.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| No logs in Kibana | Is `LOG_FILE_ENABLED=true`? |
| Vector Agent not reading | File mount correct? Check `docker logs vector-agent` |
| Kafka empty | Vector Agent connected to Kafka? Check network |
| ES no documents | Vector Aggregator connected to ES? Check `docker logs vector-aggregator` |
| Log fields missing | Check VRL transform in `vector-agent.toml` |

## Data Flow Verification Script

```bash
#!/bin/bash
echo "=== Pipeline Health Check ==="

echo "1. App health:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo "2. ES document count:"
curl -s http://localhost:9200/app-logs-*/_count | python3 -m json.tool

echo "3. Kafka topic:"
docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092 | grep app-logs

echo "4. Kibana:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:5601
```

## Next Step

Module 6 complete. In Module 7, we build the test suite — pytest with async fixtures, API integration tests, and coverage gates.
