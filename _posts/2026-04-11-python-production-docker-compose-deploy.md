---
layout: post
title: "Docker Compose Deployment"
description: "Deploy the application locally and in staging with Docker Compose, including hot-reload and observability"
categories: [python-production]
series: python-production
module: 4
module_order: 402
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-docker-compose-deploy
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

You need to run the application locally with the same configuration as staging — same container, same environment variables, same health checks. Docker Compose gives you a reproducible, single-command deployment.

## Development Compose File

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: python-app-dev
    env_file:
      - .env.staging
    ports:
      - "8000:8000"
    volumes:
      # Hot-reload: mount source code into the container
      - ./app:/app/app:ro
      - app-logs:/var/log/app
    command: >
      uvicorn app.main:app
      --host 0.0.0.0
      --port 8000
      --reload
      --log-level debug
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  app-logs:
```

Key features:
- **Hot-reload**: `./app:/app/app:ro` mount + `--reload` flag means code changes take effect instantly
- **Health check**: Container reports unhealthy if `/health` fails
- **Log volume**: Shared volume for Vector to read log files

## Environment File

```bash
# .env.staging
APP_NAME=python-production-blueprint
APP_ENV=staging
APP_VERSION=0.2.0
LOG_FORMAT=console
LOG_LEVEL=DEBUG
LOG_FILE_ENABLED=true
LOG_FILE_PATH=/var/log/app/app.log
OTEL_ENABLED=false
VAULT_ENABLED=false
```

Separate `.env.staging` and `.env.production` files keep environment-specific config out of the compose file.

## Full Infrastructure Stack

The `infrastructure/` directory contains the observability stack:

```bash
cd infrastructure

# Start everything: Kafka, Elasticsearch, Vector, Vault
docker compose up -d

# Or start individual services
docker compose -f docker-compose.kafka.yml up -d
docker compose -f docker-compose.elasticsearch.yml up -d
docker compose -f docker-compose.vector.yml up -d
docker compose -f docker-compose.vault.yml up -d
```

Then start the app:

```bash
cd ..
docker compose up --build
```

## Running the Application

```bash
# Build and start
docker compose up --build

# Detached mode
docker compose up -d --build

# View logs
docker compose logs -f app

# Check health
curl http://localhost:8000/health

# Stop
docker compose down

# Stop and remove volumes
docker compose down -v
```

## The Dockerfile

```dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir .

# Copy application code
COPY app/ app/

# Create log directory
RUN mkdir -p /var/log/app

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /var/log/app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"]
```

Security best practices:
- `python:3.11-slim` for minimal attack surface
- Non-root user (`appuser`)
- `--no-cache-dir` to reduce image size
- Built-in `HEALTHCHECK`

## Verifying the Deployment

```bash
# Health check
curl -s http://localhost:8000/health | python -m json.tool
{
    "status": "healthy",
    "service": "python-production-blueprint",
    "version": "0.2.0",
    "environment": "staging"
}

# Readiness check
curl http://localhost:8000/ready

# API test
curl -X POST http://localhost:8000/api/v1/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "price": 9.99}'

# Metrics
curl http://localhost:8000/metrics
```

## Next Step

In the next lesson, we deploy to Marathon/Mesos — an orchestrator where container stdout isn't easily accessible, requiring file-based logging.
