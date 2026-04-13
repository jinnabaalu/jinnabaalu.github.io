---
layout: post
title: "Container Security with Trivy"
description: "Scan Docker images and infrastructure-as-code for vulnerabilities using Trivy in CI"
categories: [python-production]
series: python-production
module: 6
module_order: 601
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-container-security
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Your Python code passes all tests and SAST scans, but the Docker image it runs inside contains vulnerable OS packages, outdated libraries, or insecure Kubernetes manifests. Container security scanning catches what application-level scans miss.

## Why Trivy

Trivy is a comprehensive open-source scanner that checks:
- **Container images**: OS packages (apt) and language libraries (pip)
- **Infrastructure-as-code**: Dockerfiles, Kubernetes manifests, Compose files
- **SBOM**: Software Bill of Materials generation

One tool covers multiple attack surfaces.

## Trivy Configuration

Create `.trivy.yaml` in your project root:

```yaml
severity:
  - CRITICAL
  - HIGH
  - MEDIUM

scan:
  security-checks:
    - vuln
    - config
    - secret
```

This tells Trivy to scan for vulnerabilities, misconfigurations, and embedded secrets at CRITICAL, HIGH, and MEDIUM severity levels.

## Container Image Scanning in CI

After the Docker image is built and pushed, Trivy scans it:

{% raw %}
```yaml
# .github/workflows/ci.yml
trivy-scan:
  name: Trivy Container Scan
  runs-on: ubuntu-latest
  needs: [build]
  if: github.event_name != 'pull_request'
  permissions:
    security-events: write
  steps:
    - uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ghcr.io/${{ github.repository }}:sha-${{ github.sha }}
        format: sarif
        output: trivy-results.sarif
        severity: CRITICAL,HIGH
        exit-code: 0

    - name: Upload Trivy SARIF to GitHub Security
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: trivy-results.sarif

    - name: Run Trivy (table output for logs)
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ghcr.io/${{ github.repository }}:sha-${{ github.sha }}
        format: table
        severity: CRITICAL,HIGH,MEDIUM
```
{% endraw %}

The scan runs twice:
1. **SARIF format** → uploads to GitHub Security tab for visual review
2. **Table format** → prints to CI logs for quick inspection

## Understanding Trivy Output

```
python-production-blueprint (python 3.11.9)

Total: 3 (HIGH: 2, MEDIUM: 1)

┌──────────────┬────────────────┬──────────┬───────────────┬──────────────┐
│   Library    │ Vulnerability  │ Severity │   Installed   │    Fixed     │
├──────────────┼────────────────┼──────────┼───────────────┼──────────────┤
│ cryptography │ CVE-2024-XXXXX │ HIGH     │ 41.0.0        │ 42.0.0       │
│ setuptools   │ CVE-2024-YYYYY │ HIGH     │ 69.0.0        │ 70.0.0       │
│ urllib3      │ CVE-2024-ZZZZZ │ MEDIUM   │ 2.0.0         │ 2.0.7        │
└──────────────┴────────────────┴──────────┴───────────────┴──────────────┘
```

Each row shows which package has a vulnerability, what the fix version is, and how severe it is.

## IaC Scanning

Trivy also scans Dockerfiles and Kubernetes manifests:

```yaml
iac-scan:
  name: IaC Security Scan
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Trivy IaC scan
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: config
        scan-ref: .
        format: table
        severity: CRITICAL,HIGH,MEDIUM
        exit-code: 0
```

This catches:
- Docker running as root
- Kubernetes containers without resource limits
- Missing security contexts
- Privileged container configurations

## SBOM Generation

The CI pipeline generates a Software Bill of Materials:

{% raw %}
```yaml
sbom:
  name: Generate SBOM
  runs-on: ubuntu-latest
  needs: [build]
  steps:
    - name: Generate SBOM with Trivy
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ghcr.io/${{ github.repository }}:sha-${{ github.sha }}
        format: cyclonedx
        output: sbom.json

    - name: Upload SBOM
      uses: actions/upload-artifact@v4
      with:
        name: sbom
        path: sbom.json
```
{% endraw %}

The CycloneDX format SBOM lists every component in your container — useful for compliance audits and vulnerability tracking.

## Local Scanning

Run Trivy locally before pushing:

```bash
# Install Trivy
brew install trivy

# Scan a local image
docker build -t my-app .
trivy image my-app

# Scan IaC files
trivy config .

# Scan the filesystem
trivy fs .
```

## Next Step

In the next lesson, we add dependency auditing with pip-audit — continuously checking your Python dependencies against vulnerability databases.
