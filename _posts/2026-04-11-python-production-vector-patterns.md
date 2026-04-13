---
layout: post
title: "Vector Deployment Patterns"
description: "Choose the right log collection pattern — sidecar, DaemonSet, or agent — for each deployment platform"
categories: [python-production]
series: python-production
module: 10
module_order: 1004
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-vector-patterns
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

You've deployed Vector in multiple configurations throughout this course — as a sidecar in Kubernetes, a global service in Docker Swarm, and a host agent on Marathon nodes. Each pattern has trade-offs. Understanding when to use which pattern is the difference between reliable log delivery and lost observability.

## Pattern 1: Sidecar (Kubernetes)

```yaml
# In the Pod spec
containers:
  - name: app
    volumeMounts:
      - name: app-logs
        mountPath: /var/log/app

  - name: vector-sidecar
    image: timberio/vector:0.43.1-debian
    args: ["--config", "/etc/vector/vector.toml"]
    volumeMounts:
      - name: app-logs
        mountPath: /var/log/app
        readOnly: true
volumes:
  - name: app-logs
    emptyDir:
      sizeLimit: 200Mi
```

**How it works**: App writes logs to a shared `emptyDir` volume. Vector sidecar reads from the same volume and ships logs.

| Pros | Cons |
|------|------|
| Dedicated resources per pod | Higher resource overhead |
| Isolated failure domain | One Vector per pod |
| Custom config per service | More containers to manage |

**Best for**: Applications requiring custom log processing or running in multi-tenant clusters.

## Pattern 2: DaemonSet (Kubernetes)

```yaml
# deploy/kubernetes/vector-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: vector-agent
spec:
  template:
    spec:
      containers:
        - name: vector
          image: timberio/vector:0.43.1-debian
          volumeMounts:
            - name: var-log
              mountPath: /var/log
              readOnly: true
            - name: var-lib-docker
              mountPath: /var/lib/docker/containers
              readOnly: true
      volumes:
        - name: var-log
          hostPath:
            path: /var/log
        - name: var-lib-docker
          hostPath:
            path: /var/lib/docker/containers
```

**How it works**: One Vector instance per node reads all container logs from the node's filesystem.

| Pros | Cons |
|------|------|
| Lower resource usage | Shared between all pods on node |
| Simpler management | Noisy neighbor risk |
| Node-level visibility | Generic config for all services |

**Best for**: Standard log collection where all services use the same format.

## Pattern 3: Global Service (Docker Swarm)

```yaml
# In docker-stack.yml
vector-agent:
  image: timberio/vector:0.43.1-debian
  volumes:
    - app-logs:/var/log/app:ro
  deploy:
    mode: global
```

**How it works**: Swarm runs exactly one Vector container per node. Reads from shared Docker volumes.

Equivalent to the Kubernetes DaemonSet pattern, but using Swarm's native `mode: global`.

## Pattern 4: Host Agent (Marathon/Bare Metal)

```bash
# Install Vector as a system service
curl --proto '=https' --tlsv1.2 -sSfL https://sh.vector.dev | bash

# Configure to read from host-mounted log paths
```

```toml
# /etc/vector/vector.toml
[sources.app_logs]
type = "file"
include = ["/opt/logs/python-app/*.log"]
read_from = "beginning"

[sinks.kafka]
type = "kafka"
inputs = ["app_logs"]
bootstrap_servers = "kafka:9092"
topic = "app-logs"
encoding.codec = "json"
```

**How it works**: Vector runs as a system service. App logs are written to host-mounted paths (Marathon volume mount).

| Pros | Cons |
|------|------|
| Survives container restarts | Requires host access |
| Simple configuration | Not containerized |
| Low overhead | Manual installation |

**Best for**: Marathon/Mesos, bare-metal deployments, legacy infrastructure.

## Choosing the Right Pattern

| Platform | Pattern | Reason |
|----------|---------|--------|
| Kubernetes (multi-tenant) | Sidecar | Per-service isolation |
| Kubernetes (simple) | DaemonSet | Lower overhead |
| Docker Swarm | Global service | Native Swarm pattern |
| Marathon/Mesos | Host agent | No container log access |
| Bare metal | Host agent | Direct filesystem access |

## The Agent → Aggregator Pattern

Regardless of the agent pattern, all logs flow to the aggregator:

```
App → Vector Agent (per-node/pod)
        ↓
    Kafka (buffer)
        ↓
    Vector Aggregator (centralized)
        ↓
    Elasticsearch/S3/Datadog
```

The aggregator handles:
- Log enrichment and transformation
- Fan-out to multiple destinations
- Buffering during destination outages

```toml
# vector-aggregator.toml
[sources.kafka_logs]
type = "kafka"
bootstrap_servers = "kafka:9092"
group_id = "vector-aggregator"
topics = ["app-logs"]

[transforms.parse_json]
type = "remap"
inputs = ["kafka_logs"]
source = '''
. = parse_json!(.message)
.environment = "production"
'''

[sinks.elasticsearch]
type = "elasticsearch"
inputs = ["parse_json"]
endpoints = ["http://elasticsearch:9200"]
bulk.index = "app-logs-%Y-%m-%d"
```

## Next Step

In the final module, we cover production maintenance — health checks, graceful shutdown, log rotation, dependency updates, and the complete operations runbook.
