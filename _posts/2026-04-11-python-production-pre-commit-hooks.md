---
layout: post
title: "Pre-Commit Hooks for Security"
description: "Catch secrets, lint code, and scan for vulnerabilities before every commit with pre-commit"
categories: [python-production]
series: python-production
module: 5
module_order: 505
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-pre-commit-hooks
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

A developer accidentally commits an API key. Another pushes code with a SQL injection vulnerability. A third merges a Dockerfile with a critical misconfiguration. All of these reach the repository — and CI catches them _after_ the damage is done.

Pre-commit hooks shift security checks **left** — running them on every `git commit` before code ever leaves the developer's machine.

## Install pre-commit

```bash
pip install pre-commit
```

## The Configuration

Create `.pre-commit-config.yaml` in your project root:

```yaml
repos:
  # ─── Code Quality ──────────────────────────────────
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: no-commit-to-branch
        args: ['--branch', 'main', '--branch', 'master']

  # ─── Python Linting ────────────────────────────────
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # ─── Security: Secret Scanning ─────────────────────
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.22.1
    hooks:
      - id: gitleaks

  # ─── Security: Detect secrets in code ──────────────
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # ─── Security: Python SAST ─────────────────────────
  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.3
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml', '-r', 'app/']
        additional_dependencies: ['bandit[toml]']

  # ─── Docker: Hadolint (Dockerfile linter) ──────────
  - repo: https://github.com/hadolint/hadolint
    rev: v2.13.1-beta
    hooks:
      - id: hadolint
        args: ['--ignore', 'DL3008']

  # ─── YAML Lint ─────────────────────────────────────
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        args: ['-d', 'relaxed']
```

## What Each Hook Does

| Hook | Purpose | Catches |
|------|---------|---------|
| `detect-private-key` | Scans for PEM/SSH keys | Accidental key commits |
| `gitleaks` | Regex-based secret detection | API keys, tokens, passwords |
| `detect-secrets` | Entropy-based secret detection | High-entropy strings |
| `bandit` | Python SAST | SQL injection, exec(), eval() |
| `hadolint` | Dockerfile linter | Insecure base images, bad patterns |
| `ruff` | Python linter + formatter | Code quality, style |

## Activate the Hooks

```bash
# Install hooks into .git/hooks/
pre-commit install

# Run on all files (first time)
pre-commit run --all-files
```

After installation, hooks run automatically on `git commit`. If any hook fails, the commit is blocked.

## Gitleaks Configuration

Custom rules in `.gitleaks.toml`:

```toml
[extend]
useDefault = true

[allowlist]
description = "Global allowlist"
paths = [
    '''(.*)?\.env\.example$''',
    '''(.*)?\.md$''',
]

[[rules]]
id = "vault-token"
description = "HashiCorp Vault Token"
regex = '''hvs\.[a-zA-Z0-9]{24,}'''
tags = ["vault", "token"]
```

This extends the default rules with a Vault-specific token pattern.

## Bandit Configuration

Configure in `pyproject.toml`:

```toml
[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]  # Skip assert warnings (used in tests)
```

## Workflow

```
Developer writes code
    ↓
git commit
    ↓
pre-commit hooks fire:
  ✓ trailing-whitespace
  ✓ check-yaml
  ✓ ruff (lint + format)
  ✓ gitleaks (no secrets found)
  ✓ bandit (no vulnerabilities)
  ✓ hadolint (Dockerfile OK)
    ↓
Commit succeeds → push to remote
```

If any hook fails:
```
gitleaks...............Failed
- hook id: gitleaks
- exit code: 1

Secret detected: AWS Access Key in app/config.py:15
```

The commit is blocked. Fix the issue, stage, and try again.

## Next Step

In the next lesson, we build the GitHub Actions CI pipeline that runs these same checks (plus more) on every push and pull request.
