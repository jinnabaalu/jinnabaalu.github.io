---
layout: post
title: "Docker — Containerize from Day One"
description: "Multi-stage Dockerfile, docker-compose dev workflow with hot-reload, no virtualenv needed"
categories: [python-production]
series: python-production
module: 4
module_order: 401
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-docker-setup
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

"Works on my machine" isn't a deployment strategy. Virtual environments break, system Python versions conflict, and dependency installation differs between macOS and Linux. Containers solve this by making the environment reproducible.

## Project Files

{% include project-editor.html repo="jinnabaalu/python-production-blueprint" branch="master" name="python-production-blueprint" files="Dockerfile,docker-compose.yml,docker-compose.debug.yml" %}

## The Dockerfile

The full `Dockerfile` is in the project editor above. Here's what each section does:

## Line-by-Line Breakdown

### Base image

```dockerfile
FROM python:3.11-slim AS base
```

`slim` variant — no build tools, compilers, or man pages. 150MB vs 900MB for the full image.

### Dependencies before code

```dockerfile
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app/ app/
```

Docker layers are cached. By copying `pyproject.toml` first and installing dependencies, code changes don't re-install packages. Only when dependencies change does this layer rebuild.

### Log directory

```dockerfile
RUN mkdir -p /var/log/app
```

Created inside the container for file-based logging. In Marathon or Swarm, the orchestrator mounts a host volume here so Vector can read the logs.

### Non-root user

```dockerfile
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /var/log/app
USER appuser
```

Running as root inside containers is a security vulnerability. If an attacker escapes the container, they're root on the host. `USER appuser` drops privileges.

### Built-in health check

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

Docker and orchestrators use this to determine if the container is healthy. `start-period` gives the app 10 seconds to boot before health checks begin.

## Docker Compose — Dev Workflow

The full `docker-compose.yml` is in the project editor above. Here are the key design decisions:

### Key design decisions

**No virtualenv needed.** `docker compose up` builds the image with all dependencies. Your system Python is irrelevant.

**Hot reload.** The volume mount `./app:/app/app:ro` maps your local source code into the container. `--reload` watches for changes. Edit a file, save, the server restarts inside the container.

**Read-only mount.** `:ro` prevents the container from writing to your source code directory.

**Named volume for logs.** `app-logs` persists log files across container restarts.

## Development Workflow

```bash
# Start development
docker compose up

# Rebuild after dependency changes
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f app

# Stop
docker compose down
```

## Test the Container

```bash
docker compose up -d
curl http://localhost:8000/health
# {"status":"healthy","service":"python-production-blueprint","version":"0.2.0","environment":"staging"}

curl http://localhost:8000/docs
# Swagger UI
```

## Next Step

Module 1 is complete. In Module 2, we design the API routes properly — RESTful design with FastAPI Router, error handling, and versioning.
