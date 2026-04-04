#!/usr/bin/env python3
"""Refresh GitHub repository snapshot data used by the Jekyll site."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PERSONAL_ACCOUNT = "jinnabaalu"
ORGANIZATION = "VibhuviOiO"
FEATURED_LIMIT = 8
DATA_FILE = Path(__file__).resolve().parents[1] / "_data" / "github.yml"
API_BASE = "https://api.github.com"


@dataclass
class RepoRecord:
    name: str
    owner: str
    source: str
    url: str
    description: str
    stars: int
    language: str
    updated: str


def github_get(url: str) -> tuple[list[dict[str, Any]], str | None]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jinnabalu-github-sync",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload, response.headers.get("Link")
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API request failed for {url}: {exc.code} {message}") from exc


def has_next_page(link_header: str | None) -> bool:
    if not link_header:
        return False
    return 'rel="next"' in link_header


def fetch_owned_repositories(kind: str, account: str, source: str) -> list[RepoRecord]:
    repos: list[RepoRecord] = []
    page = 1
    while True:
        if kind == "user":
            endpoint = f"{API_BASE}/users/{account}/repos"
            query = {"type": "owner", "sort": "updated", "per_page": 100, "page": page}
        else:
            endpoint = f"{API_BASE}/orgs/{account}/repos"
            query = {"type": "public", "sort": "updated", "per_page": 100, "page": page}

        url = f"{endpoint}?{urllib.parse.urlencode(query)}"
        payload, link_header = github_get(url)

        for repo in payload:
            if repo.get("fork"):
                continue
            repos.append(
                RepoRecord(
                    name=repo["name"],
                    owner=repo["owner"]["login"],
                    source=source,
                    url=repo["html_url"],
                    description=(repo.get("description") or "No description provided.").replace("\n", " ").strip(),
                    stars=int(repo.get("stargazers_count", 0)),
                    language=repo.get("language") or "Unknown",
                    updated=repo["updated_at"][:10],
                )
            )

        if not has_next_page(link_header):
            break
        page += 1

    return repos


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_yaml(personal_repos: list[RepoRecord], org_repos: list[RepoRecord]) -> str:
    all_repos = sorted(
        personal_repos + org_repos,
        key=lambda repo: (-repo.stars, repo.name.lower()),
    )
    featured = all_repos[:FEATURED_LIMIT]

    total_count = len(all_repos)
    personal_count = len(personal_repos)
    organization_count = len(org_repos)
    personal_stars = sum(repo.stars for repo in personal_repos)
    organization_stars = sum(repo.stars for repo in org_repos)
    total_stars = personal_stars + organization_stars
    last_updated = datetime.now(timezone.utc).date().isoformat()

    lines = [
        "summary:",
        f"  total_count: {total_count}",
        f"  total_stars: {total_stars}",
        f"  personal_count: {personal_count}",
        f"  personal_stars: {personal_stars}",
        f"  organization_count: {organization_count}",
        f"  organization_stars: {organization_stars}",
        f"  personal_url: {yaml_quote(f'https://github.com/{PERSONAL_ACCOUNT}')}",
        f"  organization_url: {yaml_quote(f'https://github.com/orgs/{ORGANIZATION}')}",
        f"  last_updated: {yaml_quote(last_updated)}",
        "",
        "featured_repositories:",
    ]

    for repo in featured:
        lines.extend(
            [
                f"  - name: {repo.name}",
                f"    owner: {repo.owner}",
                f"    source: {repo.source}",
                f"    url: {yaml_quote(repo.url)}",
                f"    description: {yaml_quote(repo.description)}",
                f"    stars: {repo.stars}",
                f"    language: {yaml_quote(repo.language)}",
                f"    updated: {yaml_quote(repo.updated)}",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    personal_repos = fetch_owned_repositories("user", PERSONAL_ACCOUNT, "Personal")
    org_repos = fetch_owned_repositories("org", ORGANIZATION, "Organization")

    new_content = render_yaml(personal_repos, org_repos)
    DATA_FILE.write_text(new_content, encoding="utf-8")

    print(f"Updated {DATA_FILE}")
    print(f"Personal repos      : {len(personal_repos)}")
    print(f"Organization repos  : {len(org_repos)}")
    print(f"Featured repos saved: {min(FEATURED_LIMIT, len(personal_repos) + len(org_repos))}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)