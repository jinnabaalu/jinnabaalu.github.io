---
layout: post
title: "Health Checks and Readiness Probes"
description: "Implement liveness, readiness, and startup checks that orchestrators use for self-healing and traffic routing"
categories: [python-production]
series: python-production
module: 11
module_order: 1101
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-health-checks
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Your app crashes — but the orchestrator keeps routing traffic to it. Or a dependency (database, Vault) is down, but the app keeps accepting requests it can't serve. Health checks tell the orchestrator when to restart, reroute, or hold off.

## Three Types of Probes

| Probe | Question | Action on Failure |
|-------|----------|-------------------|
| **Liveness** | Is the process alive? | Restart the container |
| **Readiness** | Can it handle traffic? | Stop routing traffic |
| **Startup** | Has it finished booting? | Block other probes |

## Implementation

```python
# app/api/routes/health.py
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@router.get("/ready")
async def readiness_check() -> dict:
    return {"status": "ready"}
```

The health endpoint is simple by design — it should respond fast, without checking external dependencies. If the process can handle HTTP requests, it's alive.

The readiness endpoint can be extended to check dependencies:

```python
@router.get("/ready")
async def readiness_check() -> dict:
    # Check critical dependencies
    checks = {
        "database": await check_database(),
        "vault": await check_vault(),
    }
    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if all_ready else "not_ready", "checks": checks}
    )
```

## Dockerfile HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

- `interval=30s`: Check every 30 seconds
- `timeout=5s`: Fail if no response in 5 seconds
- `start-period=10s`: Grace period for app startup
- `retries=3`: Mark unhealthy after 3 consecutive failures

## Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 10
  periodSeconds: 15
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 10
```

The startup probe gives up to 55 seconds (5s initial + 10×5s) to boot. Until it succeeds, liveness and readiness probes are disabled — preventing premature restarts during slow initialization.

## Marathon Health Checks

```json
"healthChecks": [
  {
    "protocol": "HTTP",
    "path": "/health",
    "portIndex": 0,
    "gracePeriodSeconds": 30,
    "intervalSeconds": 15,
    "timeoutSeconds": 5,
    "maxConsecutiveFailures": 3
  }
]
```

## Docker Swarm

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 10s
```

## Common Mistakes

1. **Health check calls external services**: If the database is down, liveness should still pass — the app process is alive. Only readiness should fail.
2. **Missing grace period**: No `start-period` means health checks fire during startup, causing restart loops.
3. **Too aggressive thresholds**: `retries: 1` with `interval: 5s` will restart on transient network blips.
4. **Health check does heavy work**: The endpoint should be lightweight — no database queries in liveness.

## Next Step

In the next lesson, we implement graceful shutdown — ensuring in-flight requests complete before the container exits.
