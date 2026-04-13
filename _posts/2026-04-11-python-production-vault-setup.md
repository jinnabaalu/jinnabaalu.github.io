---
layout: post
title: "HashiCorp Vault — Centralized Secret Management"
description: "Set up Vault, store secrets, and integrate with your Python FastAPI application using hvac"
categories: [python-production]
series: python-production
module: 9
module_order: 901
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-vault-setup
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Secrets in `.env` files get committed to Git. Secrets in environment variables are visible in `docker inspect`, process listings, and crash dumps. You need a centralized secret store with access control, audit logging, and rotation.

## HashiCorp Vault

Vault is an open-source secret management tool. Your app authenticates to Vault, requests secrets, and Vault logs every access.

```
┌──────────┐     authenticate     ┌──────────┐
│  Python  │ ──────────────────→ │  Vault   │
│   App    │ ←────────────────── │  Server  │
└──────────┘     return secrets   └──────────┘
```

## Running Vault Locally

```yaml
# infrastructure/docker-compose.vault.yml
services:
  vault:
    image: hashicorp/vault:1.15
    container_name: vault
    cap_add:
      - IPC_LOCK
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: dev-token-12345
      VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200
    ports:
      - "8200:8200"
```

Dev mode: in-memory storage, auto-unsealed, root token set via environment variable. Never use dev mode in production.

## Seeding Secrets

```bash
# Set the Vault address and token
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=dev-token-12345

# Store secrets
vault kv put secret/python-production-blueprint \
  database_url="postgresql://user:pass@db:5432/myapp" \
  api_key="sk-secret-key-12345" \
  jwt_secret="super-secret-jwt-key"

# Verify
vault kv get secret/python-production-blueprint
```

## Python Vault Client (hvac)

```python
# app/vault.py
import hvac
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def get_vault_client() -> hvac.Client:
    """Create an authenticated Vault client."""
    client = hvac.Client(url=settings.vault_url)

    if settings.vault_auth_method == "approle":
        client.auth.approle.login(
            role_id=settings.vault_role_id,
            secret_id=settings.vault_secret_id,
        )
    elif settings.vault_auth_method == "token":
        client.token = settings.vault_token
    else:
        raise ValueError(f"Unsupported auth method: {settings.vault_auth_method}")

    if not client.is_authenticated():
        raise RuntimeError("Vault authentication failed")

    return client


def read_secret(path: str | None = None, key: str | None = None) -> dict | str:
    """Read a secret from Vault KV v2 engine."""
    client = get_vault_client()
    secret_path = path or settings.vault_secret_path

    response = client.secrets.kv.v2.read_secret_version(
        path=secret_path,
        mount_point=settings.vault_mount_point,
    )

    data = response["data"]["data"]

    if key:
        if key not in data:
            raise KeyError(f"Key '{key}' not found at '{secret_path}'")
        return data[key]

    return data
```

## Loading Secrets at Startup

```python
# app/vault.py
def load_vault_secrets() -> dict:
    """Load secrets from Vault at startup. Returns empty dict if disabled."""
    if not settings.vault_enabled:
        logger.info("vault_disabled", reason="VAULT_ENABLED is false")
        return {}

    try:
        secrets = read_secret()
        logger.info(
            "vault_secrets_loaded",
            path=settings.vault_secret_path,
            keys=list(secrets.keys()) if isinstance(secrets, dict) else [],
        )
        return secrets if isinstance(secrets, dict) else {}
    except Exception:
        logger.exception("vault_secret_load_failed")
        return {}
```

In the FastAPI lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    vault_secrets = load_vault_secrets()
    app.state.vault_secrets = vault_secrets
    yield
```

Access anywhere via `request.app.state.vault_secrets["database_url"]`.

## Vault UI

Access the web UI at `http://localhost:8200` when running locally. Login with the dev token.

## Next Step

In the next lesson, we cover Vault auth methods — token auth for development and AppRole for production.
