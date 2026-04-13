---
layout: post
title: "Vector Agent — Lightweight Log Collection"
description: "Collect logs from files with Vector — no heavyweight agents, low resource usage, built in Rust"
categories: [python-production]
series: python-production
module: 8
module_order: 801
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-vector-agent
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Your app writes structured JSON logs to `/var/log/app/app.log`. These files sit on individual servers. You need to collect them, parse them, and send them to a central store — without installing a heavy agent (like Logstash) that competes for CPU and memory with your application.

## Why Vector

Vector is written in Rust — it uses ~10MB of memory and minimal CPU. Compare with Logstash (JVM, 256MB+ heap) or Fluentd (Ruby, significant overhead).

| Agent | Language | Memory | Config |
|-------|----------|--------|--------|
| Vector | Rust | ~10MB | TOML |
| Logstash | Java (JVM) | 256MB+ | Custom DSL |
| Fluentd | Ruby | 60MB+ | XML-like |
| Filebeat | Go | ~30MB | YAML |

## Vector Agent Configuration

```toml
# infrastructure/vector/vector-agent.toml

# SOURCES: Read log files
[sources.app_logs]
type = "file"
include = ["/var/log/app/*.log"]
read_from = "beginning"
fingerprint.strategy = "device_and_inode"

# TRANSFORMS: Parse JSON logs
[transforms.parse_json]
type = "remap"
inputs = ["app_logs"]
source = '''
parsed, err = parse_json(.message)
if err == null {
  . = merge(., parsed)
  del(.message)
} else {
  .raw_message = .message
  del(.message)
}
.source = "vector-agent"
.pipeline = "file-to-kafka"
.log_file = .file
'''

# SINKS: Forward to Kafka
[sinks.kafka]
type = "kafka"
inputs = ["parse_json"]
bootstrap_servers = "kafka:9092"
topic = "app-logs"
encoding.codec = "json"

[sinks.kafka.buffer]
type = "disk"
max_size = 268435456  # 256MB
when_full = "block"
```

## Architecture — Sources → Transforms → Sinks

```
[File Source] → [VRL Transform] → [Kafka Sink]
    ↓                ↓                 ↓
 Read files     Parse JSON        Send to Kafka
```

### Source: File

```toml
[sources.app_logs]
type = "file"
include = ["/var/log/app/*.log"]
read_from = "beginning"
fingerprint.strategy = "device_and_inode"
```

- Tails all `.log` files in `/var/log/app/`
- `device_and_inode` fingerprinting survives log rotation (file renamed, new file created)
- Tracks read position in a checkpoint file — restarts pick up where they left off

### Transform: VRL (Vector Remap Language)

```toml
source = '''
parsed, err = parse_json(.message)
if err == null {
  . = merge(., parsed)
  del(.message)
}
'''
```

VRL is Vector's built-in language for transforming events:
- Try to parse the log line as JSON
- If successful, merge all fields into the top-level event
- If not JSON, preserve as `raw_message`

### Sink: Kafka

```toml
[sinks.kafka]
type = "kafka"
inputs = ["parse_json"]
bootstrap_servers = "kafka:9092"
topic = "app-logs"
encoding.codec = "json"
```

Forward processed events to Kafka topic `app-logs`.

### Disk Buffer — No Lost Logs

```toml
[sinks.kafka.buffer]
type = "disk"
max_size = 268435456  # 256MB
when_full = "block"
```

If Kafka is temporarily unavailable, Vector buffers to disk. When Kafka recovers, buffered events are sent. `when_full = "block"` pauses reading (backpressure) rather than dropping logs.

## Why File-Based Collection (Not Docker Socket)

| Approach | Docker Socket | File-Based |
|----------|--------------|------------|
| Marathon | Unpredictable container names | Works via host mount |
| Docker Swarm | Socket access limited | Works via bind mounts |
| Kubernetes | Needs DaemonSet or sidecar | Works with emptyDir/hostPath |
| Security | Requires Docker socket access | Read-only file access |

File-based collection is **universal** — it works the same way on every orchestrator.

## Running Vector Agent

```yaml
# infrastructure/docker-compose.vector.yml
services:
  vector-agent:
    image: timberio/vector:0.35.0-alpine
    container_name: vector-agent
    volumes:
      - ./vector/vector-agent.toml:/etc/vector/vector.toml:ro
      - app-logs:/var/log/app:ro
      - vector-data:/var/lib/vector
```

## Next Step

In the next lesson, we add Kafka as a durable log transport — buffering logs for reliability.
