---
layout: post
title: "Marathon/Mesos Deployment"
description: "Deploy to Marathon with file-based logging, health checks, and Vault integration for legacy orchestrators"
categories: [python-production]
series: python-production
module: 10
module_order: 1001
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-marathon-deploy
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Marathon/Mesos is a legacy orchestrator still used in many enterprises. Unlike Kubernetes, it doesn't provide built-in container log aggregation. You can't `kubectl logs` — you need file-based logging with host-mounted volumes for Vector to collect.

## Marathon App Definition

```json
{
  "id": "/python-app",
  "instances": 2,
  "cpus": 0.5,
  "mem": 256,
  "container": {
    "type": "DOCKER",
    "docker": {
      "image": "your-registry.example.com/python-production-blueprint:0.2.0",
      "network": "BRIDGE",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 0,
          "protocol": "tcp",
          "name": "http",
          "labels": {
            "VIP_0": "/python-app:8000"
          }
        }
      ],
      "forcePullImage": true
    },
    "volumes": [
      {
        "containerPath": "/var/log/app",
        "hostPath": "/opt/logs/python-app",
        "mode": "RW"
      }
    ]
  }
}
```

Key decisions:
- **`hostPort: 0`**: Marathon assigns a random host port — service discovery handles routing
- **Volume mount**: `/var/log/app` maps to `/opt/logs/python-app` on the host so Vector can read log files
- **VIP**: Virtual IP for internal service mesh routing

## Environment Variables

```json
{
  "env": {
    "APP_NAME": "python-production-blueprint",
    "APP_ENV": "production",
    "APP_VERSION": "0.2.0",
    "APP_PORT": "8000",
    "APP_WORKERS": "2",
    "LOG_FORMAT": "json",
    "LOG_LEVEL": "INFO",
    "LOG_FILE_ENABLED": "true",
    "LOG_FILE_PATH": "/var/log/app/app.log",
    "OTEL_ENABLED": "true",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://jaeger.service.consul:4317",
    "OTEL_SERVICE_NAME": "python-production-blueprint",
    "VAULT_ENABLED": "true",
    "VAULT_URL": "http://vault.service.consul:8200",
    "VAULT_AUTH_METHOD": "approle",
    "VAULT_MOUNT_POINT": "secret",
    "VAULT_SECRET_PATH": "python-production-blueprint"
  }
}
```

Critical settings for Marathon:
- `LOG_FILE_ENABLED: "true"` — enables `RotatingFileHandler` (since stdout is unreliable)
- `LOG_FILE_PATH: "/var/log/app/app.log"` — matches the volume mount
- Service discovery uses Consul addresses (`.service.consul`)

## Health Checks

```json
{
  "healthChecks": [
    {
      "protocol": "HTTP",
      "path": "/health",
      "portIndex": 0,
      "gracePeriodSeconds": 30,
      "intervalSeconds": 15,
      "timeoutSeconds": 5,
      "maxConsecutiveFailures": 3
    },
    {
      "protocol": "HTTP",
      "path": "/ready",
      "portIndex": 0,
      "gracePeriodSeconds": 30,
      "intervalSeconds": 30,
      "timeoutSeconds": 5,
      "maxConsecutiveFailures": 5
    }
  ]
}
```

Two health checks:
- **`/health`**: Liveness — is the app running? Checked every 15s, 3 failures = restart
- **`/ready`**: Readiness — is it accepting traffic? More lenient (5 failures) for startup
- **`gracePeriodSeconds: 30`**: Gives the app time to start before health checks begin

## Upgrade Strategy

```json
{
  "upgradeStrategy": {
    "minimumHealthCapacity": 0.5,
    "maximumOverCapacity": 0.25
  }
}
```

During a rolling update:
- At least 50% of instances stay healthy at all times
- Up to 25% extra capacity during the transition
- With 2 instances: one old instance stays running while one new instance starts

## Deployment Commands

```bash
# Deploy
curl -X POST http://marathon.example.com/v2/apps \
  -H "Content-Type: application/json" \
  -d @deploy/marathon/marathon-app.json

# Update
curl -X PUT http://marathon.example.com/v2/apps/python-app \
  -H "Content-Type: application/json" \
  -d @deploy/marathon/marathon-app.json

# Scale
curl -X PUT http://marathon.example.com/v2/apps/python-app \
  -H "Content-Type: application/json" \
  -d '{"instances": 4}'

# Check status
curl http://marathon.example.com/v2/apps/python-app | python -m json.tool
```

## Log Collection with Vector

On each Marathon agent, Vector runs as a system service reading from the host-mounted log directory:

```toml
# /etc/vector/vector.toml (on Marathon agents)
[sources.app_logs]
type = "file"
include = ["/opt/logs/python-app/*.log"]
read_from = "beginning"
```

This is the file-based logging pattern we built in Module 4 — the `RotatingFileHandler` writes JSON lines to `/var/log/app/app.log`, which is host-mounted at `/opt/logs/python-app/`, where Vector picks them up.

## Next Step

In the next lesson, we deploy to Docker Swarm — a simpler alternative to Kubernetes with native Docker tooling.
