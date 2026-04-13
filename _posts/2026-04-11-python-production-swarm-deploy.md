---
layout: post
title: "Docker Swarm Deployment"
description: "Deploy with Docker Swarm using rolling updates, secrets management, and global Vector agents"
categories: [python-production]
series: python-production
module: 10
module_order: 1002
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-swarm-deploy
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

You need container orchestration with rolling updates, health checks, and secrets — but Kubernetes is overkill for your team size. Docker Swarm uses the same Docker CLI you already know, with built-in orchestration.

## Stack Definition

```yaml
# deploy/docker-swarm/docker-stack.yml
version: "3.9"

services:
  app:
    image: your-registry.example.com/python-production-blueprint:0.2.0
    environment:
      APP_NAME: python-production-blueprint
      APP_ENV: production
      APP_VERSION: "0.2.0"
      APP_PORT: "8000"
      APP_WORKERS: "2"
      LOG_FORMAT: json
      LOG_LEVEL: INFO
      LOG_FILE_ENABLED: "true"
      LOG_FILE_PATH: /var/log/app/app.log
      OTEL_ENABLED: "true"
      OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger:4317
      OTEL_SERVICE_NAME: python-production-blueprint
      VAULT_ENABLED: "true"
      VAULT_URL: http://vault:8200
      VAULT_AUTH_METHOD: approle
      VAULT_MOUNT_POINT: secret
      VAULT_SECRET_PATH: python-production-blueprint
    ports:
      - "8000:8000"
    volumes:
      - app-logs:/var/log/app
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 30s
        failure_action: rollback
        order: start-first
      rollback_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
        reservations:
          cpus: "0.25"
          memory: 128M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s
    secrets:
      - vault_role_id
      - vault_secret_id
    networks:
      - observability
```

## Rolling Update Strategy

```yaml
update_config:
  parallelism: 1       # Update one container at a time
  delay: 30s           # Wait 30s between updates
  failure_action: rollback  # Auto-rollback on failure
  order: start-first   # Start new before stopping old
```

`start-first` ensures zero downtime — the new container must pass health checks before the old one is removed. If the new container fails, Swarm automatically rolls back.

## Secrets Management

Swarm has built-in secrets support — no Vault sidecar needed:

```yaml
secrets:
  vault_role_id:
    external: true
  vault_secret_id:
    external: true
```

Create secrets before deploying:

```bash
# Create secrets
echo "your-role-id" | docker secret create vault_role_id -
echo "your-secret-id" | docker secret create vault_secret_id -

# Secrets are available in the container at /run/secrets/
# vault_role_id → /run/secrets/vault_role_id
# vault_secret_id → /run/secrets/vault_secret_id
```

## Vector Agent — Global Mode

```yaml
  vector-agent:
    image: timberio/vector:0.43.1-debian
    volumes:
      - ./vector/vector-agent.toml:/etc/vector/vector.toml:ro
      - app-logs:/var/log/app:ro
    deploy:
      mode: global        # One instance per Swarm node
      resources:
        limits:
          memory: 128M
    networks:
      - observability
```

`mode: global` deploys one Vector agent on every Swarm node — ensuring log collection wherever the app containers run.

## Vector Aggregator

```yaml
  vector-aggregator:
    image: timberio/vector:0.43.1-debian
    volumes:
      - ./vector/vector-aggregator.toml:/etc/vector/vector.toml:ro
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 128M
    networks:
      - observability
```

The aggregator receives logs from all agents, enriches them, and forwards to Kafka/Elasticsearch.

## Networking

```yaml
networks:
  observability:
    driver: overlay
    attachable: true
```

The `overlay` network spans all Swarm nodes — containers on different hosts can communicate by service name.

## Deployment Commands

```bash
# Initialize Swarm (first time)
docker swarm init

# Deploy the stack
docker stack deploy -c deploy/docker-swarm/docker-stack.yml python-app

# Check services
docker stack services python-app

# View logs
docker service logs python-app_app -f

# Scale
docker service scale python-app_app=4

# Update image (triggers rolling update)
docker service update --image your-registry/python-production-blueprint:0.3.0 python-app_app

# Remove stack
docker stack rm python-app
```

## Monitoring the Rollout

{% raw %}
```bash
# Watch the update progress
docker service ps python-app_app --format "table {{.ID}}\t{{.Name}}\t{{.Image}}\t{{.CurrentState}}"

# Check for rollback
docker service inspect python-app_app --format '{{.UpdateStatus.State}}'
```
{% endraw %}

## Next Step

In the next lesson, we deploy to Kubernetes — the industry standard for container orchestration with advanced features like HPA, ingress, and sidecar patterns.
