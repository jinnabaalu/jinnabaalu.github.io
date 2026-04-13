---
layout: post
title: "Kafka — Durable Log Transport"
description: "Buffer logs in Kafka for reliability and fan-out to multiple sinks without data loss"
categories: [python-production]
series: python-production
module: 8
module_order: 802
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-kafka-log-transport
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

If Elasticsearch goes down, logs are lost. If the network between Vector and Elasticsearch drops, logs are lost. You need a buffer between collection and storage — something durable that holds logs until the downstream system recovers.

## Why Kafka

Kafka is a distributed commit log. Once a message is written, it's persisted to disk and replicated. It can buffer millions of messages while Elasticsearch is offline.

```
Vector Agent → Kafka → Vector Aggregator → Elasticsearch
                 ↓
            Persists to disk
            Retains for 7 days
            Multiple consumers
```

## Kafka in the Pipeline

```yaml
# infrastructure/docker-compose.kafka.yml
services:
  kafka:
    image: bitnami/kafka:3.7
    container_name: kafka
    environment:
      KAFKA_CFG_NODE_ID: 0
      KAFKA_CFG_PROCESS_ROLES: controller,broker
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: 0@kafka:9093
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CFG_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_CFG_LOG_RETENTION_HOURS: 168  # 7 days
    ports:
      - "9092:9092"
    volumes:
      - kafka-data:/bitnami/kafka
```

### KRaft Mode (No ZooKeeper)

This uses Kafka's built-in KRaft consensus — no ZooKeeper dependency. Simpler to deploy and operate.

## How Kafka Helps the Log Pipeline

| Scenario | Without Kafka | With Kafka |
|----------|--------------|------------|
| ES goes down 1 hour | 1 hour of logs lost | 0 logs lost (buffered) |
| Spike in log volume | Vector overwhelms ES | Kafka absorbs the spike |
| Add second consumer | Change Vector config | Add consumer group |
| Network partition | Logs dropped | Kafka retries |

## Log Retention

```
KAFKA_CFG_LOG_RETENTION_HOURS: 168  # 7 days
```

Kafka retains messages for 7 days regardless of consumption. If your aggregator is down for a weekend, all logs are still there on Monday.

## Topic: app-logs

Vector Agent writes to the `app-logs` topic. Vector Aggregator reads from it. The topic is auto-created on first write.

For production, pre-create topics with explicit partition counts:

```bash
kafka-topics.sh --create \
  --topic app-logs \
  --partitions 6 \
  --replication-factor 3 \
  --bootstrap-server kafka:9092
```

## Consumer Groups

```toml
# Vector Aggregator config
[sources.kafka]
type = "kafka"
group_id = "vector-aggregator"
```

The `group_id` enables Kafka to track what's been consumed. If Vector Aggregator restarts, it resumes from the last committed offset — no duplicates, no gaps.

## Next Step

In the next lesson, we build the Vector Aggregator — reading from Kafka, transforming events, and shipping to Elasticsearch.
