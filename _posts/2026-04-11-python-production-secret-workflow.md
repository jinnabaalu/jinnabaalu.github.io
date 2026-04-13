---
layout: post
title: "Secret Workflow — Local to Production"
description: ".env for local, Vault for staging/prod — a practical workflow for managing secrets across environments"
categories: [python-production]
series: python-production
module: 9
module_order: 903
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-secret-workflow
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Different environments need different secret strategies. Local dev needs simplicity. Staging needs Vault testing. Production needs audit-grade security. You need one codebase that works across all three.

## The Workflow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    Local     │    │   Staging    │    │  Production  │
│              │    │              │    │              │
│  .env file   │    │ Vault token  │    │ Vault AppRole│
│  VAULT=false │    │ VAULT=true   │    │ VAULT=true   │
│  Defaults ok │    │ Dev token    │    │ Short-lived  │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Local Development

```bash
# .env.staging (committed to repo — no real secrets)
VAULT_ENABLED=false
LOG_LEVEL=DEBUG
LOG_FORMAT=console
```

Vault is disabled. Config comes from `.env` defaults. No Vault server needed.

```bash
docker compose up
# App starts with defaults — no secrets required
```

## Staging

```bash
# Start Vault + seed secrets
cd infrastructure && docker compose up -d vault

# .env.staging or environment vars
VAULT_ENABLED=true
VAULT_URL=http://vault:8200
VAULT_AUTH_METHOD=token
VAULT_TOKEN=dev-token-12345
```

Vault runs in dev mode. Token auth is fine — this is a test environment.

## Production

```bash
# Injected by CI/CD or orchestrator — never in files
VAULT_ENABLED=true
VAULT_URL=https://vault.internal:8200
VAULT_AUTH_METHOD=approle
VAULT_ROLE_ID=abc-123-role-id
VAULT_SECRET_ID=xyz-789-secret-id  # Generated per-deploy
```

### Secret ID Injection Patterns

**Kubernetes:**
```yaml
env:
  - name: VAULT_SECRET_ID
    valueFrom:
      secretKeyRef:
        name: app-vault-creds
        key: secret-id
```

**Docker Swarm:**
```yaml
secrets:
  - vault_secret_id
environment:
  VAULT_SECRET_ID_FILE: /run/secrets/vault_secret_id
```

**Marathon:**
```json
{
  "env": {
    "VAULT_SECRET_ID": {"secret": "vault-secret-id"}
  }
}
```

## What NOT to Put in Vault

Not everything belongs in Vault:

| Vault | Environment Variable |
|-------|---------------------|
| Database credentials | App name |
| API keys | Log level |
| JWT signing keys | Port number |
| Encryption keys | Feature flags |
| Third-party tokens | Concurrency settings |

**Rule:** If it's a secret (would cause damage if exposed), use Vault. If it's configuration (different per environment but not sensitive), use env vars.

## Accessing Secrets in Routes

```python
@router.get("/external-data")
async def get_external_data(request: Request):
    secrets = request.app.state.vault_secrets
    api_key = secrets.get("external_api_key", "")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.external.com/data",
            headers={"Authorization": f"Bearer {api_key}"},
        )
    return response.json()
```

## Fail-Safe Design

```python
def load_vault_secrets() -> dict:
    if not settings.vault_enabled:
        return {}
    try:
        secrets = read_secret()
        return secrets
    except Exception:
        logger.exception("vault_secret_load_failed")
        return {}  # App starts without secrets — better than crash
```

The app **logs the failure** but doesn't crash. This prevents a Vault outage from taking down your application. Some features may be degraded, but the health endpoint still works.

## Next Step

Module 3 complete. In Module 4, we implement structured logging — JSON logs with context binding, correlation IDs, and dual output for different deployment patterns.
