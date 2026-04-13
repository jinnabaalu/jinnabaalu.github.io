---
layout: post
title: "GitHub Actions CI Pipeline"
description: "Automate testing, linting, SAST scanning, and Docker builds on every push with GitHub Actions"
categories: [python-production]
series: python-production
module: 5
module_order: 506
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-github-actions-ci
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Pre-commit hooks run on the developer's machine — but a developer might skip them (`--no-verify`), use a different machine, or miss a configuration. The CI pipeline is the authoritative gate: every push and PR must pass before code can be merged.

## Pipeline Architecture

```
Push/PR → Test & Lint → SAST → Secret Scan → Dependency Audit
                                                      ↓
                                              Build Docker Image
                                                      ↓
                                    Trivy Container Scan → IaC Scan → SBOM
```

Each stage runs in parallel where possible. The Docker build only runs after all quality gates pass.

## The CI Workflow

{% raw %}
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```
{% endraw %}

## Job 1: Test & Lint

{% raw %}
```yaml
jobs:
  test:
    name: Test & Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint with ruff
        run: |
          ruff check app/ tests/
          ruff format --check app/ tests/

      - name: Run tests
        run: pytest --cov=app --cov-report=xml --cov-report=term-missing

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
```
{% endraw %}

This installs the project with dev dependencies, lints, runs tests with coverage, and uploads the report.

## Job 2: SAST with Bandit

{% raw %}
```yaml
  sast:
    name: SAST - Bandit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install bandit
        run: pip install "bandit[toml]"

      - name: Run Bandit SAST scan
        run: bandit -c pyproject.toml -r app/ -f json -o bandit-report.json || true

      - name: Upload Bandit report
        uses: actions/upload-artifact@v4
        with:
          name: bandit-report
          path: bandit-report.json
```
{% endraw %}

Bandit scans Python code for common security issues: `eval()`, hardcoded passwords, SQL injection, insecure deserialization.

## Job 3: Secret Scanning

{% raw %}
```yaml
  secret-scan:
    name: Secret Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for scanning

      - name: Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
{% endraw %}

`fetch-depth: 0` ensures Gitleaks scans the entire Git history — not just the latest commit.

## Job 4: Dependency Audit

{% raw %}
```yaml
  dependency-audit:
    name: Dependency Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: pip-audit (vulnerability scan)
        run: pip-audit --format json --output pip-audit-report.json || true

      - name: Upload audit report
        uses: actions/upload-artifact@v4
        with:
          name: pip-audit-report
          path: pip-audit-report.json
```
{% endraw %}

`pip-audit` checks every installed package against the Python Advisory Database (PyPI) and OSV for known vulnerabilities.

## Job 5: Build Docker Image

{% raw %}
```yaml
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [test, sast, secret-scan, dependency-audit]
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```
{% endraw %}

Key decisions:
- `needs: [test, sast, secret-scan, dependency-audit]` — build only after all checks pass
- PR builds don't push (`push: false` when `event_name == 'pull_request'`)
- GHA cache makes subsequent builds faster

## The Pipeline Flow

```
           test ──────────┐
           sast ──────────┤
     secret-scan ─────────┼──→ build ──→ trivy-scan ──→ sbom
  dependency-audit ───────┘         └──→ iac-scan
```

Jobs 1-4 run in parallel. Build waits for all four. Post-build scans run after the image is available.

## Next Step

In the next lesson, we add container security scanning with Trivy — checking the built Docker image for OS and library vulnerabilities.
