#!/usr/bin/env python3
"""Refresh Medium RSS and external article snapshot data used by the Jekyll site."""

from __future__ import annotations

import email.utils
import html
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


FEED_URL = "https://medium.com/feed/@jinnabaalu"
RSS_FILE = Path(__file__).resolve().parents[1] / "medium-rss.xml"
DATA_FILE = Path(__file__).resolve().parents[1] / "_data" / "external-articles.yml"


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
            "User-Agent": "jinnabalu-medium-sync",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Medium RSS request failed for {url}: {exc.code} {message}") from exc


def normalize_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url.strip())
    path = parts.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit((parts.scheme or "https", parts.netloc, path, "", ""))


def clean_text(value: str | None) -> str:
    return html.unescape((value or "").strip())


def parse_inline_list(value: str) -> list[str]:
    inner = value.strip()[1:-1].strip()
    if not inner:
        return []
    return [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]


def parse_scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return parse_inline_list(value)
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if value.isdigit():
        return int(value)
    return value


def parse_external_articles(text: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("- "):
            if current is not None:
                entries.append(current)
            current = {}
            remainder = line[2:]
            if remainder.strip():
                key, value = remainder.split(":", 1)
                current[key.strip()] = parse_scalar(value)
            continue
        if current is not None and line.startswith("  "):
            key, value = stripped.split(":", 1)
            current[key.strip()] = parse_scalar(value)

    if current is not None:
        entries.append(current)
    return entries


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


KNOWN_LABELS = {
    "aws": "AWS",
    "ebs": "EBS",
    "eks": "EKS",
    "npm": "NPM",
    "kafka": "Kafka",
    "docker": "Docker",
    "docker-compose": "Docker",
    "elasticsearch": "Elasticsearch",
    "cassandra": "Cassandra",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "ansible": "Ansible",
    "cloudflare": "Cloudflare",
    "caddy": "Caddy",
    "python": "Python",
    "git": "Git",
    "kubernetes": "Kubernetes",
    "macos": "macOS",
    "open-source": "Open Source",
}


def format_category(tag: str) -> str:
    normalized = tag.strip().lower()
    if normalized in KNOWN_LABELS:
        return KNOWN_LABELS[normalized]
    words = normalized.replace("_", " ").replace("-", " ").split()
    return " ".join(word.upper() if len(word) <= 3 else word.capitalize() for word in words) or tag


def source_from_url(url: str) -> str:
    host = urllib.parse.urlsplit(url).netloc.lower()
    if "devgenius" in host:
        return "Dev Genius"
    return "Medium"


def parse_medium_entries(rss_text: str) -> list[dict[str, object]]:
    root = ET.fromstring(rss_text)
    channel = root.find("channel")
    if channel is None:
        raise RuntimeError("Invalid Medium RSS format: missing channel")

    entries: list[dict[str, object]] = []
    for item in channel.findall("item"):
        link = clean_text(item.findtext("link"))
        title = clean_text(item.findtext("title"))
        pub_date = clean_text(item.findtext("pubDate"))
        parsed_date = email.utils.parsedate_to_datetime(pub_date)
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
        categories = []
        seen = set()
        for cat in item.findall("category"):
            label = format_category(clean_text(cat.text))
            if label and label not in seen:
                categories.append(label)
                seen.add(label)
        entries.append(
            {
                "date": parsed_date.date().isoformat(),
                "title": title,
                "url": normalize_url(link),
                "source": source_from_url(normalize_url(link)),
                "categories": categories,
            }
        )
    return entries


def merge_articles(existing_entries: list[dict[str, object]], medium_entries: list[dict[str, object]]) -> list[dict[str, object]]:
    existing_by_url = {
        normalize_url(str(entry.get("url", ""))): dict(entry)
        for entry in existing_entries
    }

    merged_by_url: dict[str, dict[str, object]] = dict(existing_by_url)
    for item in medium_entries:
        url = normalize_url(str(item["url"]))
        if url in merged_by_url:
            existing = merged_by_url[url]
            existing.setdefault("date", item["date"])
            existing.setdefault("title", item["title"])
            existing.setdefault("url", item["url"])
            existing.setdefault("source", item["source"])
            if not existing.get("categories"):
                existing["categories"] = item["categories"]
            continue

        merged_by_url[url] = {
            "date": item["date"],
            "title": item["title"],
            "url": item["url"],
            "source": item["source"],
            "categories": item["categories"],
        }

    all_entries = list(merged_by_url.values())
    all_entries.sort(key=lambda entry: (str(entry.get("date", "")), str(entry.get("title", "")).lower()))
    return all_entries


def render_articles(entries: list[dict[str, object]]) -> str:
    lines = [
        "# External articles published on Medium, Dev Genius, etc.",
        "# These appear in the Tech Timeline as links (no local content duplication)",
        "#",
        "# Add entries with: date, title, url, source, categories",
    ]

    for entry in entries:
        categories = ", ".join(str(item) for item in entry.get("categories", []))
        lines.extend(
            [
                "",
                f"- date: {entry.get('date', '')}",
                f"  title: {yaml_quote(str(entry.get('title', '')))}",
                f"  url: {yaml_quote(str(entry.get('url', '')))}",
                f"  source: {entry.get('source', 'Medium')}",
            ]
        )
        if "claps" in entry:
            lines.append(f"  claps: {int(entry['claps'])}")
        lines.append(f"  categories: [{categories}]")

    return "\n".join(lines) + "\n"


def main() -> int:
    rss_text = fetch_text(FEED_URL)
    RSS_FILE.write_text(rss_text, encoding="utf-8")

    existing_entries = parse_external_articles(DATA_FILE.read_text(encoding="utf-8"))
    medium_entries = parse_medium_entries(rss_text)
    merged_entries = merge_articles(existing_entries, medium_entries)
    DATA_FILE.write_text(render_articles(merged_entries), encoding="utf-8")

    print(f"Updated {RSS_FILE}")
    print(f"Updated {DATA_FILE}")
    print(f"Medium feed items : {len(medium_entries)}")
    print(f"External articles : {len(merged_entries)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)