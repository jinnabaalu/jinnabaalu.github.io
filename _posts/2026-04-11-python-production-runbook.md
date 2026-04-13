---
layout: post
title: "Production Operations Runbook"
description: "The complete reference for deploying, monitoring, troubleshooting, and maintaining the Python production blueprint"
categories: [python-production]
series: python-production
module: 11
module_order: 1105
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-runbook
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## Purpose

This is the operational reference for running `python-production-blueprint` in production. Keep it updated as your system evolves.

## Quick Reference

| Item | Value |
|------|-------|
| **Repository** | `github.com/jinnabaalu/python-production-blueprint` |
| **Port** | 8000 |
| **Health** | `GET /health` |
| **Readiness** | `GET /ready` |
| **Metrics** | `GET /metrics` |
| **API Docs** | `GET /docs` (staging only) |
| **Log format** | JSON (structlog) |
| **Tracing** | OpenTelemetry → Jaeger |

## Deployment Checklist

Before deploying to production:

- [ ] All CI checks pass (tests, SAST, secret scan, dependency audit)
- [ ] Docker image built and scanned by Trivy
- [ ] No CRITICAL or HIGH vulnerabilities
- [ ] Vault secrets configured (AppRole credentials)
- [ ] Environment variables set correctly
- [ ] Health check endpoints responding
- [ ] Monitoring dashboards updated
- [ ] Rollback plan documented

## Environment Variables

```bash
# Required
APP_NAME=python-production-blueprint
APP_ENV=production
APP_VERSION=0.2.0

# Logging
LOG_FORMAT=json
LOG_LEVEL=INFO
LOG_FILE_ENABLED=true          # true for Marathon, optional for K8s
LOG_FILE_PATH=/var/log/app/app.log

# OpenTelemetry
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
OTEL_SERVICE_NAME=python-production-blueprint

# Vault
VAULT_ENABLED=true
VAULT_URL=http://vault:8200
VAULT_AUTH_METHOD=approle
VAULT_MOUNT_POINT=secret
VAULT_SECRET_PATH=python-production-blueprint
```

## Deploy Commands

### Docker Compose
```bash
docker compose up -d --build
docker compose logs -f app
```

### Marathon
```bash
curl -X PUT http://marathon.example.com/v2/apps/python-app \
  -H "Content-Type: application/json" \
  -d @deploy/marathon/marathon-app.json
```

### Docker Swarm
```bash
docker stack deploy -c deploy/docker-swarm/docker-stack.yml python-app
docker service ps python-app_app
```

### Kubernetes
```bash
kubectl apply -f deploy/kubernetes/
kubectl rollout status deployment/python-production-blueprint -n python-app
```

## Rollback Procedures

### Docker Swarm
```bash
docker service update --rollback python-app_app
```

### Kubernetes
```bash
kubectl rollout undo deployment/python-production-blueprint -n python-app
kubectl rollout history deployment/python-production-blueprint -n python-app
```

### Marathon
```bash
# Deploy previous version
curl -X PUT http://marathon.example.com/v2/apps/python-app \
  -H "Content-Type: application/json" \
  -d '{"container":{"docker":{"image":"your-registry/python-production-blueprint:0.1.0"}}}'
```

## Troubleshooting

### App not starting

```bash
# Check container logs
docker logs python-app-dev
kubectl logs -l app=python-production-blueprint -n python-app

# Common causes:
# - Vault unreachable → VAULT_ENABLED=false to bypass
# - Port conflict → check APP_PORT
# - Missing env vars → check ConfigMap/env_file
```

### Health check failing

```bash
# Test manually
curl -v http://localhost:8000/health

# If 000/connection refused → app not started, check logs
# If 500 → app error, check structured logs for stack trace
# If timeout → check CPU/memory limits, app may be overloaded
```

### Missing logs

```bash
# Check if file logging is enabled
curl http://localhost:8000/health  # Triggers a log entry

# Check the log file directly
docker exec python-app-dev cat /var/log/app/app.log

# Check Vector is running
docker ps | grep vector

# Check Vector metrics
curl http://vector:8686/health
```

### High memory usage

```bash
# Check container metrics
docker stats python-app-dev

# Kubernetes
kubectl top pods -n python-app

# Common causes:
# - Too many workers → reduce APP_WORKERS
# - Memory leak → check for unclosed connections
# - Log buffer overflow → check LOG_FILE_MAX_BYTES
```

### Vault connection errors

```bash
# Test Vault connectivity
curl http://vault:8200/v1/sys/health

# Check AppRole credentials
curl -X POST http://vault:8200/v1/auth/approle/login \
  -d '{"role_id":"your-role-id","secret_id":"your-secret-id"}'

# Bypass Vault temporarily
VAULT_ENABLED=false
```

## Monitoring

### Key Metrics to Watch

| Metric | Healthy Range | Alert Threshold |
|--------|---------------|-----------------|
| `http_requests_total` | Varies | Sudden drop = outage |
| Request latency p99 | < 500ms | > 1s |
| Error rate (5xx) | < 0.1% | > 1% |
| CPU usage | < 70% | > 85% |
| Memory usage | < 80% | > 90% |
| Pod restarts | 0 | > 2 in 5 min |

### Dashboards

- **Prometheus**: `http://prometheus:9090` — raw metrics
- **Jaeger**: `http://jaeger:16686` — distributed traces
- **Kibana**: `http://kibana:5601` — log search and analysis
- **Grafana**: Import dashboards for FastAPI + Vector

### Log Search (Kibana)

```
# Find errors
level:ERROR AND service:python-production-blueprint

# Trace a specific request
request_id:"abc-123-def"

# Find slow requests
duration_ms:>1000

# Find recent deploys
event:application_starting
```

## Scaling

### Horizontal Scaling

```bash
# Kubernetes
kubectl scale deployment/python-production-blueprint --replicas=4 -n python-app

# Docker Swarm
docker service scale python-app_app=4

# Marathon
curl -X PUT http://marathon.example.com/v2/apps/python-app \
  -d '{"instances": 4}'
```

### Vertical Scaling

Adjust resource limits in deployment manifests:

```yaml
# Kubernetes
resources:
  requests:
    cpu: 200m      # Up from 100m
    memory: 256Mi  # Up from 128Mi
  limits:
    cpu: 1000m     # Up from 500m
    memory: 512Mi  # Up from 256Mi
```

## Maintenance Windows

### Scheduled Maintenance Checklist

- [ ] Notify stakeholders
- [ ] Scale up before patching (extra capacity)
- [ ] Apply updates to one node/pod at a time
- [ ] Verify health checks pass after each update
- [ ] Monitor error rates for 15 minutes
- [ ] Scale back to normal capacity

## Architecture Summary

```
Client → Ingress/HAProxy → FastAPI App (N replicas)
                                  ↓
                          Structured Logs → Vector Agent
                          Traces → Jaeger (OTLP)       ↓
                          Metrics → Prometheus      Kafka
                                                       ↓
                                              Vector Aggregator
                                                       ↓
                                              Elasticsearch → Kibana
```

## Course Complete

You've built a production-grade Python application from scratch — covering API design, configuration, secrets management, structured logging, distributed tracing, log pipelines, testing, security scanning, multi-platform deployment, and operational maintenance.

The [python-production-blueprint](https://github.com/jinnabaalu/python-production-blueprint) repository is your reference implementation. Fork it, adapt it to your stack, and ship with confidence.
