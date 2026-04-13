---
layout: post
title: "Graceful Shutdown"
description: "Handle SIGTERM properly so in-flight requests complete and resources are released during deployments"
categories: [python-production]
series: python-production
module: 11
module_order: 1102
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-graceful-shutdown
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

During a rolling update, the orchestrator sends SIGTERM to the old container. If the app exits immediately, in-flight requests get dropped — users see 502 errors, partial writes corrupt data, and WebSocket connections break unexpectedly.

## The Shutdown Sequence

```
Orchestrator sends SIGTERM
    ↓
Readiness probe fails → stop new traffic
    ↓
App finishes in-flight requests
    ↓
Cleanup: close connections, flush logs
    ↓
Process exits (code 0)
    ↓
If still running after grace period → SIGKILL
```

## FastAPI Lifespan Handler

FastAPI's lifespan context manager handles both startup and shutdown:

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.logging_config import get_logger, setup_logging
from app.vault import load_vault_secrets

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ─── Startup ─────────────────────────────────
    vault_secrets = load_vault_secrets()
    app.state.vault_secrets = vault_secrets

    logger.info(
        "application_starting",
        app_name=settings.app_name,
        environment=settings.app_env,
        version=settings.app_version,
    )

    yield  # App runs here, handling requests

    # ─── Shutdown ────────────────────────────────
    logger.info("application_shutting_down")
    # Close database connections, flush buffers, etc.
```

Everything after `yield` runs when SIGTERM is received. Uvicorn handles:
1. Stopping the accept loop (no new connections)
2. Waiting for in-flight requests to complete
3. Calling the lifespan shutdown

## Uvicorn Signal Handling

Uvicorn gracefully handles SIGTERM by default:

```bash
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"]
```

When SIGTERM arrives, Uvicorn:
1. Stops accepting new connections
2. Waits for active requests to finish (up to the timeout)
3. Calls the lifespan shutdown handler
4. Exits cleanly

## Kubernetes Grace Period

```yaml
# deploy/kubernetes/deployment.yaml
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 30
```

This gives 30 seconds between SIGTERM and SIGKILL. The timeline:

```
T=0s   SIGTERM received, readiness probe fails
T=0-5s Kubernetes removes pod from Service endpoints
T=5-25s In-flight requests complete
T=25s  Lifespan shutdown runs (flush logs, close connections)
T=30s  SIGKILL if still running
```

## Docker Compose

Docker Compose sends SIGTERM and waits 10 seconds by default:

```yaml
services:
  app:
    stop_grace_period: 30s  # Override the 10s default
```

## Docker Swarm

```yaml
deploy:
  update_config:
    order: start-first  # New container starts before old stops
```

`start-first` is crucial — the new container is healthy before the old one receives SIGTERM.

## Marathon

```json
{
  "upgradeStrategy": {
    "minimumHealthCapacity": 0.5,
    "maximumOverCapacity": 0.25
  }
}
```

Marathon maintains capacity during upgrades. The default SIGTERM timeout is 3 seconds — configure `taskKillGracePeriodSeconds` for longer:

```json
{
  "taskKillGracePeriodSeconds": 30
}
```

## What to Clean Up on Shutdown

| Resource | Cleanup Action |
|----------|---------------|
| Database connections | Close connection pool |
| HTTP clients | Close `httpx.AsyncClient` sessions |
| Log buffers | Flush any buffered log entries |
| OpenTelemetry | Flush trace/metric exporters |
| File handles | Close cleanly |
| Background tasks | Cancel and await completion |

## Testing Graceful Shutdown

```bash
# Start the container
docker compose up -d

# Send SIGTERM
docker compose stop app

# Watch logs for clean shutdown
docker compose logs app | tail -5
```

Expected log output:
```json
{"event": "application_shutting_down", "timestamp": "2024-01-15T10:30:00Z"}
```

## Next Step

In the next lesson, we configure log rotation — preventing log files from consuming all available disk space on Marathon/host-mount deployments.
