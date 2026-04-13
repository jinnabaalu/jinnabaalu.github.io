---
layout: post
title: "Environment-Based Config with pydantic-settings"
description: "Type-safe configuration from environment variables with validation, defaults, and .env file support"
categories: [python-production]
series: python-production
module: 2
module_order: 202
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-config-management
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Hardcoded config values (`host = "localhost"`) break in production. Scattered `os.getenv()` calls across the codebase are untyped, unvalidated, and easy to forget. You need config that's type-safe, validated at startup, and environment-aware.

## pydantic-settings — Config as a Model

```python
# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "python-production-blueprint"
    app_env: str = "staging"  # staging | production
    app_version: str = "0.1.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_workers: int = 1

    # Logging
    log_format: str = "json"  # json | console
    log_level: str = "INFO"
    log_file_enabled: bool = False
    log_file_path: str = "/var/log/app/app.log"
    log_file_max_bytes: int = 52428800  # 50MB
    log_file_backup_count: int = 5

    # OpenTelemetry
    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "python-production-blueprint"

    # Vault
    vault_enabled: bool = False
    vault_url: str = "http://localhost:8200"
    vault_token: str = ""
    vault_mount_point: str = "secret"
    vault_secret_path: str = "python-production-blueprint"
    vault_auth_method: str = "token"  # token | approle
    vault_role_id: str = ""
    vault_secret_id: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
```

## How It Works

### Automatic Environment Mapping

Each field maps to an **uppercase environment variable**:

| Field | Environment Variable |
|-------|---------------------|
| `app_name` | `APP_NAME` |
| `log_level` | `LOG_LEVEL` |
| `vault_enabled` | `VAULT_ENABLED` |
| `otel_exporter_otlp_endpoint` | `OTEL_EXPORTER_OTLP_ENDPOINT` |

### Type Coercion

pydantic-settings automatically converts string env vars to the correct Python type:

```bash
export APP_PORT=9000           # str → int
export VAULT_ENABLED=true      # str → bool
export LOG_FILE_MAX_BYTES=104857600  # str → int
```

### Validation at Startup

If you set `APP_PORT=not_a_number`, the app **fails to start** with a clear error — not midway through handling a request.

### Defaults for Development

Every field has a sensible default:
- `vault_enabled: bool = False` — Vault off by default
- `otel_enabled: bool = False` — Tracing off until explicitly enabled
- `log_format: str = "json"` — JSON logging for machines

## .env Files

```bash
# .env.staging
APP_NAME=python-production-blueprint
APP_ENV=staging
LOG_LEVEL=DEBUG
LOG_FORMAT=console
LOG_FILE_ENABLED=true
LOG_FILE_PATH=/var/log/app/app.log
VAULT_ENABLED=false
OTEL_ENABLED=false
```

```bash
# .env.production
APP_NAME=python-production-blueprint
APP_ENV=production
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_ENABLED=true
VAULT_ENABLED=true
VAULT_URL=https://vault.internal:8200
VAULT_AUTH_METHOD=approle
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
```

### Priority Order

1. **Environment variables** (highest)
2. **`.env` file** (from `model_config`)
3. **Field defaults** (lowest)

This means Docker env vars override `.env` file values — exactly what you want in Kubernetes or Swarm.

## Computed Properties

```python
@property
def is_production(self) -> bool:
    return self.app_env == "production"
```

Use properties for derived values. The Swagger UI is disabled in production using this:

```python
docs_url="/docs" if not settings.is_production else None,
```

## `extra = "ignore"`

```python
model_config = {"extra": "ignore"}
```

Extra environment variables (like `PATH`, `HOME`) are silently ignored instead of causing validation errors.

## Using Settings

Import the singleton anywhere:

```python
from app.config import settings

# Use it
if settings.otel_enabled:
    setup_tracing()
```

The `settings` object is created once at import time. All modules share the same instance.

## Next Step

In the next lesson, we integrate HashiCorp Vault for centralized secret management — no more secrets in `.env` files.
