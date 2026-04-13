---
layout: post
title: "Dual Output — Stdout and File Logging"
description: "Stdout for containers, RotatingFileHandler for Marathon and host-mount scenarios — dual logging output"
categories: [python-production]
series: python-production
module: 3
module_order: 304
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-dual-logging
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

In Docker and Kubernetes, you log to stdout — the orchestrator captures it. But in Marathon (Mesos), container names are unpredictable and Docker socket access is unreliable. You need logs written to a **host-mounted file path** where Vector can read them.

The solution: log to both stdout AND file, controlled by environment variables.

## The Implementation

```python
# app/logging_config.py (continued from previous lesson)
import os
from logging.handlers import RotatingFileHandler

def setup_logging() -> None:
    # ... (processors and structlog.configure from previous lesson)

    # File handler — always uses JSON regardless of stdout format
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),  # Always JSON for machines
        ],
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Always add stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_formatter)
    root_logger.addHandler(stdout_handler)

    # Conditionally add file handler
    if settings.log_file_enabled:
        log_dir = os.path.dirname(settings.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=settings.log_file_path,
            maxBytes=settings.log_file_max_bytes,    # 50MB
            backupCount=settings.log_file_backup_count,  # 5 files
            encoding="utf-8",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    root_logger.setLevel(log_level)
```

## Configuration

```bash
# Enable file logging (Marathon, host-mount)
LOG_FILE_ENABLED=true
LOG_FILE_PATH=/var/log/app/app.log
LOG_FILE_MAX_BYTES=52428800    # 50MB per file
LOG_FILE_BACKUP_COUNT=5        # Keep 5 rotated files
```

## RotatingFileHandler — Why

| Feature | Why |
|---------|-----|
| `maxBytes=52428800` | 50MB per file prevents disk exhaustion |
| `backupCount=5` | Keeps `app.log`, `app.log.1`, ..., `app.log.5` |
| Automatic rotation | When `app.log` hits 50MB, it becomes `app.log.1` |
| Total max | 50MB × 6 = 300MB maximum disk usage for logs |

## File Handler Always Uses JSON

```python
file_formatter = structlog.stdlib.ProcessorFormatter(
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.JSONRenderer(),  # Always JSON
    ],
)
```

Even if stdout uses `ConsoleRenderer` (for developer readability), the file handler writes JSON. Vector, Fluentd, and log aggregators need machine-parseable format.

## Deployment Patterns

### Docker / Kubernetes (stdout only)

```bash
LOG_FILE_ENABLED=false
```

Logs go to stdout → Docker captures → Kubernetes log driver or fluentd collects.

### Marathon (file only matters for collection)

```bash
LOG_FILE_ENABLED=true
LOG_FILE_PATH=/var/log/app/app.log
```

Logs go to both stdout and file. Vector Agent reads `/var/log/app/*.log` from the host-mounted path.

### Docker Swarm (both)

```bash
LOG_FILE_ENABLED=true
```

Swarm captures stdout, and Vector reads files via bind mounts. Belt and suspenders.

## Volume Mount Setup

```yaml
# docker-compose
volumes:
  - app-logs:/var/log/app

# Marathon
"volumes": [
  {"containerPath": "/var/log/app", "hostPath": "/var/log/marathon/app", "mode": "RW"}
]

# Kubernetes
volumeMounts:
  - name: logs
    mountPath: /var/log/app
```

## Disk Safety in Dockerfile

```dockerfile
RUN mkdir -p /var/log/app
RUN adduser --disabled-password appuser && chown -R appuser:appuser /var/log/app
```

The directory exists and is writable by the non-root user. If the volume mount fails, the app can still write (though files won't persist).

## Next Step

Module 4 complete. In Module 5, we add distributed tracing with OpenTelemetry and Prometheus metrics — find where your requests slow down.
