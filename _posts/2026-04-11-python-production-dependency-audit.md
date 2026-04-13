---
layout: post
title: "Dependency Auditing with pip-audit"
description: "Continuously scan Python dependencies for known vulnerabilities using pip-audit and Dependency-Track"
categories: [python-production]
series: python-production
module: 6
module_order: 602
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-dependency-audit
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Your direct dependencies might be secure, but their transitive dependencies may have known CVEs. A project with 10 direct dependencies can pull in 50+ transitive ones. `pip-audit` checks _all_ of them against vulnerability databases.

## pip-audit in CI

The CI pipeline runs `pip-audit` on every push:

```yaml
# .github/workflows/ci.yml
dependency-audit:
  name: Dependency Audit
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

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

## Understanding pip-audit Output

```bash
pip-audit
```

```
Found 2 known vulnerabilities in 1 package
Name         Version ID                  Fix Versions
------------ ------- ------------------- ------------
cryptography 41.0.0  GHSA-xxxx-yyyy-zzzz 42.0.0
cryptography 41.0.0  PYSEC-2024-XXXX     42.0.0
```

Each row shows the package, its current version, the advisory ID, and the version that fixes it.

## Local Usage

```bash
# Install
pip install pip-audit

# Audit current environment
pip-audit

# JSON output
pip-audit --format json

# Strict mode (exit code 1 on any finding)
pip-audit --strict

# Audit a requirements file
pip-audit -r requirements.txt
```

## Fixing Vulnerabilities

When pip-audit finds a vulnerability:

1. **Check the advisory**: Visit the GHSA/PYSEC link for details
2. **Update the package**: `pip install --upgrade cryptography`
3. **Test**: Run your test suite to verify nothing breaks
4. **Pin**: Update version constraints in `pyproject.toml`

```toml
# pyproject.toml
dependencies = [
    "fastapi>=0.115",
    "cryptography>=42.0",  # Updated from 41.0 for CVE fix
]
```

## Dependency-Track for Continuous Monitoring

The blueprint includes a Dependency-Track stack for ongoing SBOM-based vulnerability monitoring:

```yaml
# devsecops/dependency-track/docker-compose.yml
services:
  dtrack-apiserver:
    image: dependencytrack/apiserver:4.12.3
    environment:
      ALPINE_DATABASE_MODE: external
      ALPINE_DATABASE_URL: jdbc:postgresql://postgres:5432/dtrack
      ALPINE_DATABASE_DRIVER: org.postgresql.Driver
      ALPINE_DATABASE_USERNAME: dtrack
      ALPINE_DATABASE_PASSWORD: dtrack
    ports:
      - "8081:8080"

  dtrack-frontend:
    image: dependencytrack/frontend:4.12.3
    ports:
      - "8082:8080"
    environment:
      API_BASE_URL: http://localhost:8081

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: dtrack
      POSTGRES_USER: dtrack
      POSTGRES_PASSWORD: dtrack
    volumes:
      - dtrack-db:/var/lib/postgresql/data
```

Upload the SBOM generated in CI:

```bash
# Upload SBOM to Dependency-Track
curl -X "POST" "http://localhost:8081/api/v1/bom" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "project=python-production-blueprint" \
  -F "bom=@sbom.json"
```

Dependency-Track then continuously monitors your SBOM against new CVEs — alerting when a previously-safe dependency becomes vulnerable.

## License Compliance

The scheduled security scan also checks licenses:

```yaml
# .github/workflows/security-scan.yml
- name: Check licenses
  run: |
    pip-licenses --format=json --output-file=licenses.json
    pip-licenses --format=table
    # Fail on copyleft licenses
    pip-licenses --fail-on="GPL;AGPL;LGPL" || echo "WARNING: Copyleft license detected"
```

This ensures you don't accidentally include a GPL dependency in a proprietary project.

## Next Step

In the next lesson, we set up scheduled security scans — daily automated checks that catch newly-disclosed vulnerabilities in your existing dependencies.
