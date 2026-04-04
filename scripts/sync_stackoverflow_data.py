#!/usr/bin/env python3
"""Refresh Stack Overflow snapshot data used by the Jekyll site."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


USER_ID = 4348824
TOP_TAG_LIMIT = 6
TOP_ANSWER_LIMIT = 10
SUMMARY = "High-signal answers focused on Docker, Elasticsearch, and production operations."
API_BASE = "https://api.stackexchange.com/2.3"
DATA_FILE = Path(__file__).resolve().parents[1] / "_data" / "stackoverflow.yml"


def api_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    query = dict(params)
    query["site"] = "stackoverflow"
    key = os.getenv("STACKEXCHANGE_KEY")
    if key:
        query["key"] = key

    url = f"{API_BASE}{path}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "jinnabalu-stackoverflow-sync",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Stack Exchange API request failed for {url}: {exc.code} {message}") from exc

    if "error_message" in payload:
        raise RuntimeError(f"Stack Exchange API error for {url}: {payload['error_message']}")
    return payload


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def format_date(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat()


def render_yaml(profile: dict[str, Any], top_tags: list[dict[str, Any]], answers: list[dict[str, Any]], question_map: dict[int, dict[str, Any]]) -> str:
    last_updated = datetime.now(timezone.utc).date().isoformat()
    reputation = int(profile.get("reputation", 0))
    badge_counts = profile.get("badge_counts", {})

    lines = [
        "# Stack Overflow profile snapshot.",
        "# Refreshed from the Stack Exchange API.",
        "",
        "profile:",
        f"  display_name: {yaml_quote(profile.get('display_name', 'Jinna Baalu'))}",
        f"  user_id: {int(profile.get('user_id', USER_ID))}",
        f"  profile_url: {yaml_quote(profile.get('link', f'https://stackoverflow.com/users/{USER_ID}'))}",
        f"  website_url: {yaml_quote(profile.get('website_url', 'https://jinnabalu.com'))}",
        f"  reputation: {reputation}",
        f"  reputation_display: {yaml_quote(f'{reputation:,}')}",
        "  badges:",
        f"    gold: {int(badge_counts.get('gold', 0))}",
        f"    silver: {int(badge_counts.get('silver', 0))}",
        f"    bronze: {int(badge_counts.get('bronze', 0))}",
        f"  summary: {yaml_quote(SUMMARY)}",
        f"  last_updated: {yaml_quote(last_updated)}",
        "",
        "top_tags:",
    ]

    for tag in top_tags[:TOP_TAG_LIMIT]:
        lines.extend(
            [
                f"  - name: {tag.get('tag_name', '')}",
                f"    answer_count: {int(tag.get('answer_count', 0))}",
                f"    answer_score: {int(tag.get('answer_score', 0))}",
            ]
        )

    lines.extend(["", "top_answers:"])

    for answer in answers[:TOP_ANSWER_LIMIT]:
        question = question_map.get(int(answer.get("question_id", 0)), {})
        tags = question.get("tags", [])
        answer_link = answer.get("link") or f"https://stackoverflow.com/a/{int(answer.get('answer_id', 0))}"
        lines.extend(
            [
                f"  - answer_id: {int(answer.get('answer_id', 0))}",
                f"    answer_url: {yaml_quote(answer_link)}",
                f"    question_id: {int(answer.get('question_id', 0))}",
                f"    question_url: {yaml_quote(question.get('link', ''))}",
                f"    title: {yaml_quote(question.get('title', ''))}",
                f"    score: {int(answer.get('score', 0))}",
                f"    accepted: {'true' if answer.get('is_accepted') else 'false'}",
                f"    created: {yaml_quote(format_date(int(answer.get('creation_date', 0))))}",
                f"    tags: [{', '.join(tags)}]",
                "",
            ]
        )

    if lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> int:
    profile_payload = api_get(f"/users/{USER_ID}", {"pagesize": 1})
    tag_payload = api_get(f"/users/{USER_ID}/top-answer-tags", {"pagesize": TOP_TAG_LIMIT})
    answer_payload = api_get(
        f"/users/{USER_ID}/answers",
        {"pagesize": TOP_ANSWER_LIMIT, "order": "desc", "sort": "votes", "filter": "default"},
    )

    answers = answer_payload.get("items", [])
    question_ids = [str(int(answer["question_id"])) for answer in answers if answer.get("question_id")]
    question_payload = {"items": []}
    if question_ids:
        question_payload = api_get(
            f"/questions/{';'.join(question_ids)}",
            {"pagesize": len(question_ids), "order": "desc", "sort": "activity", "filter": "default"},
        )

    question_map = {int(item["question_id"]): item for item in question_payload.get("items", [])}
    profile_items = profile_payload.get("items", [])
    if not profile_items:
        raise RuntimeError("No Stack Overflow profile data returned")

    new_content = render_yaml(profile_items[0], tag_payload.get("items", []), answers, question_map)
    DATA_FILE.write_text(new_content, encoding="utf-8")

    print(f"Updated {DATA_FILE}")
    print(f"Top tags saved   : {min(TOP_TAG_LIMIT, len(tag_payload.get('items', [])))}")
    print(f"Top answers saved: {min(TOP_ANSWER_LIMIT, len(answers))}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)