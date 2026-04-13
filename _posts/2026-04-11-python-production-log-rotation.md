---
layout: post
title: "Log Rotation and Disk Management"
description: "Configure RotatingFileHandler and Vector to prevent log files from filling up disk on production hosts"
categories: [python-production]
series: python-production
module: 11
module_order: 1103
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-log-rotation
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

File-based logging on Marathon hosts writes continuously. Without rotation, a single app instance can fill a 50GB disk in days. When disk is full, the host becomes unresponsive — affecting all containers on that node.

## Python RotatingFileHandler

The blueprint uses Python's built-in `RotatingFileHandler`:

```python
# app/logging_config.py
from logging.handlers import RotatingFileHandler

if settings.log_file_enabled:
    log_dir = os.path.dirname(settings.log_file_path)
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=settings.log_file_path,
        maxBytes=settings.log_file_max_bytes,     # 50MB
        backupCount=settings.log_file_backup_count, # 5 files
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
```

## Configuration

```python
# app/config.py
class Settings(BaseSettings):
    log_file_enabled: bool = False
    log_file_path: str = "/var/log/app/app.log"
    log_file_max_bytes: int = 52428800   # 50MB per file
    log_file_backup_count: int = 5       # Keep 5 rotated files
```

With these settings:
- **Active file**: `app.log` (up to 50MB)
- **Rotated files**: `app.log.1`, `app.log.2`, ... `app.log.5`
- **Maximum disk usage**: 300MB (6 × 50MB)

When `app.log` reaches 50MB:
1. `app.log.5` is deleted
2. `app.log.4` → `app.log.5`
3. `app.log.3` → `app.log.4`
4. `app.log.2` → `app.log.3`
5. `app.log.1` → `app.log.2`
6. `app.log` → `app.log.1`
7. New `app.log` starts empty

## Tuning for Your Workload

| Workload | maxBytes | backupCount | Total Disk |
|----------|----------|-------------|------------|
| Low traffic API | 10MB | 3 | 40MB |
| Medium API | 50MB | 5 | 300MB |
| High traffic | 100MB | 10 | 1.1GB |
| Debug mode | 50MB | 2 | 150MB |

Formula: `total_disk = maxBytes × (backupCount + 1)`

## Vector File Source Configuration

Vector must be configured to handle rotated files:

```toml
# vector-agent.toml
[sources.app_logs]
type = "file"
include = ["/var/log/app/*.log"]
read_from = "beginning"
ignore_older_secs = 86400  # Ignore files older than 24h
```

`include = ["*.log"]` catches both `app.log` and rotated files like `app.log.1`. Vector tracks read positions with checkpoints, so it won't re-read data after rotation.

## Kubernetes EmptyDir Limits

In Kubernetes, the sidecar pattern uses `emptyDir` — set a size limit to prevent disk exhaustion:

```yaml
volumes:
  - name: app-logs
    emptyDir:
      sizeLimit: 200Mi
```

If the volume exceeds 200Mi, Kubernetes evicts the pod. This is a last-resort safety net — the `RotatingFileHandler` should prevent it from ever reaching this limit.

## Docker Volume Cleanup

For Docker Compose and Swarm:

```bash
# Check volume usage
docker system df -v

# Clean up unused volumes
docker volume prune

# Check specific volume
docker volume inspect python-app_app-logs
```

## Monitoring Disk Usage

Add a disk usage check to your readiness endpoint:

```python
import shutil

@router.get("/ready")
async def readiness_check() -> dict:
    disk = shutil.disk_usage("/var/log/app")
    disk_free_pct = (disk.free / disk.total) * 100

    return {
        "status": "ready" if disk_free_pct > 5 else "not_ready",
        "disk_free_percent": round(disk_free_pct, 1),
    }
```

If the log volume is nearly full, the readiness check fails — the orchestrator stops routing traffic before disk-related errors cascade.

## Environment-Specific Overrides

```bash
# Marathon: file logging required
LOG_FILE_ENABLED=true
LOG_FILE_MAX_BYTES=52428800
LOG_FILE_BACKUP_COUNT=5

# Kubernetes: stdout logging preferred, file as backup for sidecar
LOG_FILE_ENABLED=true
LOG_FILE_MAX_BYTES=10485760   # 10MB (sidecar reads quickly)
LOG_FILE_BACKUP_COUNT=2

# Docker Compose local: stdout only
LOG_FILE_ENABLED=false
```

## Next Step

In the next lesson, we set up dependency update workflows — keeping your Python packages and Docker base images current with automated tooling.
