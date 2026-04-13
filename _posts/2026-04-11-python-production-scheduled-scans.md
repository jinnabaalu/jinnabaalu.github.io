---
layout: post
title: "Scheduled Security Scans"
description: "Run daily automated vulnerability scans for dependencies, containers, and license compliance"
categories: [python-production]
series: python-production
module: 6
module_order: 603
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-scheduled-scans
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Your CI pipeline scans on every push — but what about vulnerabilities discovered _after_ you deployed? A new CVE published on Tuesday affects a library you pushed on Monday. Without scheduled scans, you won't know until the next code change triggers CI.

## Scheduled Security Workflow

{% raw %}
```yaml
# .github/workflows/security-scan.yml
name: Security Scan (Scheduled)

on:
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual trigger

env:
  PYTHON_VERSION: "3.11"
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```
{% endraw %}

`workflow_dispatch` lets you trigger the scan manually from the GitHub Actions UI — useful when a critical CVE is announced.

## Job 1: Dependency Vulnerability Scan

{% raw %}
```yaml
jobs:
  dependency-scan:
    name: Dependency Vulnerability Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: pip-audit
        run: pip-audit --format json --output pip-audit-report.json
        continue-on-error: true

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: scheduled-pip-audit
          path: pip-audit-report.json
```
{% endraw %}

`continue-on-error: true` ensures the workflow completes and uploads the report even if vulnerabilities are found — you want the full picture, not a failed-fast partial scan.

## Job 2: Container Image Rescan

{% raw %}
```yaml
  container-rescan:
    name: Rescan Latest Container Image
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - name: Trivy scan latest image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:main
          format: sarif
          output: trivy-scheduled.sarif
          severity: CRITICAL,HIGH
        continue-on-error: true

      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-scheduled.sarif
        continue-on-error: true
```
{% endraw %}

This rescans the `main` tag — the image currently running in production. New CVEs affecting Alpine packages, Python runtime, or bundled libraries appear here.

## Job 3: License Compliance

{% raw %}
```yaml
  license-check:
    name: License Compliance
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install pip-licenses

      - name: Check licenses
        run: |
          pip-licenses --format=json --output-file=licenses.json
          pip-licenses --format=table
          # Fail on copyleft licenses
          pip-licenses --fail-on="GPL;AGPL;LGPL" || echo "WARNING: Copyleft license detected"

      - name: Upload license report
        uses: actions/upload-artifact@v4
        with:
          name: license-report
          path: licenses.json
```
{% endraw %}

This catches:
- New dependencies that introduce copyleft licenses
- License changes in dependency updates
- Missing license metadata

## Complete DevSecOps Pipeline Summary

| Layer | Tool | Trigger | Catches |
|-------|------|---------|---------|
| Pre-commit | Gitleaks, Bandit, Ruff | `git commit` | Secrets, SAST, style |
| CI - Test | pytest, ruff | Push/PR | Regressions, lint |
| CI - SAST | Bandit | Push/PR | Python vulnerabilities |
| CI - Secrets | Gitleaks | Push/PR | Leaked credentials |
| CI - Deps | pip-audit | Push/PR | Known CVEs in packages |
| CI - Build | Docker Buildx | Push (after gates) | Build failures |
| CI - Container | Trivy | After build | OS/lib CVEs in image |
| CI - IaC | Trivy config | Push/PR | Insecure manifests |
| CI - SBOM | Trivy/CycloneDX | After build | Component inventory |
| Scheduled | pip-audit, Trivy | Daily 2 AM | New CVE disclosures |
| Scheduled | pip-licenses | Daily 2 AM | License violations |
| Continuous | Dependency-Track | SBOM upload | Ongoing vulnerability feed |

This multi-layered approach ensures vulnerabilities are caught at the earliest possible stage — from developer workstation to production runtime.

## Next Step

In the next module, we deploy our application to multiple platforms — starting with Docker Compose for local and staging environments.
