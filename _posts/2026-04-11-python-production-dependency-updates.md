---
layout: post
title: "Dependency Updates and Maintenance"
description: "Keep Python packages, Docker images, and GitHub Actions up to date with automated tooling"
categories: [python-production]
series: python-production
module: 11
module_order: 1104
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-dependency-updates
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Dependencies go stale. A package you installed 3 months ago now has a security fix. The Docker base image has a critical CVE. GitHub Actions you use are deprecated. Manual updating is tedious and error-prone — automated tooling keeps you current.

## Dependabot for Python

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 5
    labels:
      - dependencies
      - python
    commit-message:
      prefix: "deps(python):"

  # Docker base image
  - package-ecosystem: docker
    directory: /
    schedule:
      interval: weekly
    labels:
      - dependencies
      - docker
    commit-message:
      prefix: "deps(docker):"

  # GitHub Actions
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    labels:
      - dependencies
      - ci
    commit-message:
      prefix: "deps(actions):"
```

Dependabot opens PRs automatically for:
- Python package updates (checks `pyproject.toml`)
- Docker base image updates (`FROM python:3.11-slim`)
- GitHub Actions version bumps (`actions/checkout@v4`)

## Reviewing Dependency PRs

When a Dependabot PR arrives:

1. **Read the changelog**: What changed? Breaking changes?
2. **Check CI**: All tests pass? Coverage unchanged?
3. **Check security**: Does this fix a CVE? (Dependabot labels security fixes)
4. **Merge**: If green, merge. If not, investigate.

```bash
# Merge Dependabot PRs via CLI
gh pr list --label dependencies
gh pr merge 42 --squash
```

## Manual Dependency Audit

```bash
# Check for outdated packages
pip list --outdated

# Audit for vulnerabilities
pip-audit

# Update a specific package
pip install --upgrade fastapi

# Update all (use with caution)
pip install --upgrade -e ".[dev]"

# Regenerate lock/constraints if using pip-compile
pip-compile pyproject.toml
```

## Docker Base Image Updates

The `python:3.11-slim` image receives security patches regularly. Check for updates:

{% raw %}
```bash
# Pull latest
docker pull python:3.11-slim

# Check image digest
docker inspect python:3.11-slim --format='{{.RepoDigests}}'

# Rebuild with latest base
docker build --pull --no-cache -t my-app .
```
{% endraw %}

`--pull` forces Docker to fetch the latest base image. `--no-cache` ensures all layers rebuild with upgraded system packages.

## Version Pinning Strategy

```toml
# pyproject.toml
dependencies = [
    "fastapi>=0.115,<1.0",        # Pin major, allow minor/patch
    "uvicorn[standard]>=0.34",     # Allow all compatible updates
    "structlog>=24.0",             # Allow all compatible updates
    "pydantic-settings>=2.0,<3.0", # Pin major
]
```

Pin strategy:
- **Major version**: Pin to prevent breaking changes
- **Minor/patch**: Allow updates for bug fixes and security patches
- **Security-critical packages**: Update immediately regardless of version

## Pre-commit Hook Updates

```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Test the updates
pre-commit run --all-files
```

Run `pre-commit autoupdate` monthly to keep Ruff, Bandit, Gitleaks, and other hooks current.

## Maintenance Calendar

| Task | Frequency | Tool |
|------|-----------|------|
| Python dependency updates | Weekly (automated) | Dependabot |
| Docker base image updates | Weekly (automated) | Dependabot |
| GitHub Actions updates | Weekly (automated) | Dependabot |
| Pre-commit hook updates | Monthly (manual) | `pre-commit autoupdate` |
| pip-audit full scan | Daily (automated) | Scheduled security scan |
| Trivy container scan | Daily (automated) | Scheduled security scan |
| License compliance check | Daily (automated) | Scheduled security scan |
| Vector version update | Quarterly (manual) | Check Vector changelog |

## Next Step

In the final lesson, we compile everything into a production operations runbook — the single document your team needs for day-to-day operations.
