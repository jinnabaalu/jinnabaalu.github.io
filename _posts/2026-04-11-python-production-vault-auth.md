---
layout: post
title: "Vault Auth Methods — Token vs AppRole"
description: "Token auth for development, AppRole for production — when and why to use each Vault authentication method"
categories: [python-production]
series: python-production
module: 9
module_order: 902
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-vault-auth
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Token auth works for development, but a single static token in production is a security risk — if leaked, it gives full access forever. Production needs machine identity with short-lived credentials.

## Token Auth (Development)

```python
if settings.vault_auth_method == "token":
    client.token = settings.vault_token
```

```bash
# .env.staging
VAULT_AUTH_METHOD=token
VAULT_TOKEN=dev-token-12345
```

**When:** Local development, CI pipelines, dev Vault in Docker.
**Risk:** Token is long-lived, single factor, stored in env vars.

## AppRole Auth (Production)

AppRole is Vault's machine-to-machine auth. It uses two credentials:

- **Role ID** — identifies the application (like a username). Can be shared.
- **Secret ID** — proves identity (like a password). Short-lived, consumed on use.

```python
if settings.vault_auth_method == "approle":
    client.auth.approle.login(
        role_id=settings.vault_role_id,
        secret_id=settings.vault_secret_id,
    )
```

### Setting Up AppRole in Vault

```bash
# Enable AppRole auth
vault auth enable approle

# Create a policy
vault policy write app-policy - <<EOF
path "secret/data/python-production-blueprint" {
  capabilities = ["read"]
}
EOF

# Create a role
vault write auth/approle/role/python-app \
  token_policies="app-policy" \
  token_ttl=1h \
  token_max_ttl=4h \
  secret_id_ttl=24h

# Get role ID (stable — bake into config)
vault read auth/approle/role/python-app/role-id

# Generate secret ID (short-lived — inject at deploy time)
vault write -f auth/approle/role/python-app/secret-id
```

### How It Flows

```
1. Deploy injects VAULT_ROLE_ID + VAULT_SECRET_ID into container
2. App calls vault.auth.approle.login(role_id, secret_id)
3. Vault validates, returns a short-lived TOKEN
4. App uses TOKEN to read secrets
5. Token expires after TTL — app re-authenticates if needed
```

### Why AppRole Is Safer

| Feature | Token | AppRole |
|---------|-------|---------|
| Credentials | 1 (token) | 2 (role_id + secret_id) |
| Token lifetime | Unlimited (unless set) | TTL-bounded (e.g., 1 hour) |
| Rotation | Manual | Secret ID consumed on use |
| Audit | Who used the token? | Role + IP + timestamp |
| Blast radius | Full token access | Policy-scoped |

## Policy — Least Privilege

```hcl
# infrastructure/vault/policies/app-policy.hcl
path "secret/data/python-production-blueprint" {
  capabilities = ["read"]
}
```

The app can only **read** its own secrets. It can't write, delete, or access other paths.

## Config by Environment

```bash
# .env.staging
VAULT_ENABLED=true
VAULT_AUTH_METHOD=token
VAULT_TOKEN=dev-token-12345

# .env.production
VAULT_ENABLED=true
VAULT_AUTH_METHOD=approle
VAULT_ROLE_ID=<from vault read>
VAULT_SECRET_ID=<injected at deploy>
```

## Next Step

In the next lesson, we put it all together — the secret workflow from local development through staging to production.
