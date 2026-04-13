---
layout: post
title: "Test Coverage and CI Integration"
description: "Measure code coverage with pytest-cov, set thresholds, and integrate with GitHub Actions"
categories: [python-production]
series: python-production
module: 5
module_order: 504
image: assets/img/courses/python-production.png
author: jinnabalu
toc: true
permalink: /courses/python-production-test-coverage
githublink: https://github.com/jinnabaalu/python-production-blueprint
---

## The Problem

Tests exist, but are they testing _enough_? Without coverage metrics, critical code paths (error handling, edge cases) stay untested. Coverage measurement shows what you've missed.

## Install pytest-cov

The blueprint already includes it as a dev dependency:

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=6.0",
    "httpx>=0.28",
]
```

## Running with Coverage

```bash
# Basic coverage report
pytest --cov=app

# With line-by-line detail
pytest --cov=app --cov-report=term-missing

# Generate XML for CI (Codecov, GitHub Actions)
pytest --cov=app --cov-report=xml --cov-report=term-missing
```

Sample output:

```
---------- coverage: platform darwin, python 3.11 ----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
app/__init__.py                       0      0   100%
app/config.py                        20      0   100%
app/logging_config.py                28      4    86%   82-85
app/main.py                          25      0   100%
app/vault.py                         35     18    49%   25-42
app/api/models/items.py              10      0   100%
app/api/routes/health.py              8      0   100%
app/api/routes/items.py              30      2    93%   45-46
app/middleware/logging_middleware.py  22      0   100%
app/telemetry/metrics.py             18      3    83%   30-32
app/telemetry/tracing.py             20      8    60%   15-22
---------------------------------------------------------------
TOTAL                               216     35    84%
```

## Reading the Report

- **Stmts**: Total executable statements
- **Miss**: Lines not executed by any test
- **Cover**: Percentage covered
- **Missing**: Exact line numbers to focus on

Low-coverage files tell you where to write tests next. `vault.py` at 49% means Vault integration paths need testing.

## Setting Coverage Thresholds

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["app"]
omit = ["app/telemetry/*"]  # Optional: exclude tracing setup from coverage

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__",
    "if TYPE_CHECKING",
]
```

`fail_under = 80` makes `pytest --cov` exit with a non-zero code if coverage drops below 80% — your CI pipeline will fail.

## CI Integration

In the GitHub Actions pipeline, coverage runs automatically:

```yaml
# .github/workflows/ci.yml (test job)
- name: Run tests
  run: pytest --cov=app --cov-report=xml --cov-report=term-missing

- name: Upload coverage
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: coverage.xml
```

The XML report can be consumed by:
- **Codecov** for PR annotations
- **SonarQube** for quality gates
- **GitHub Actions** to display in job summaries

## What to Cover vs What to Skip

| Worth covering | OK to skip |
|----------------|------------|
| API routes and response codes | Third-party library internals |
| Model validation (Pydantic) | OpenTelemetry setup boilerplate |
| Middleware (correlation IDs) | Logger configuration details |
| Error handling paths | `if __name__ == "__main__"` blocks |
| Config loading + defaults | |

100% coverage is not the goal. **80-90% with meaningful tests** is better than 100% with brittle assertions.

## Next Step

In the next module, we shift to DevSecOps — starting with pre-commit hooks that catch security issues _before_ code reaches your repository.
