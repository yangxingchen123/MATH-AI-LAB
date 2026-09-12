"""Render Frozen-field Markdown for create operations."""

from __future__ import annotations

from datetime import date
from typing import Any

import yaml


def today() -> str:
    return date.today().isoformat()


def dump_front(data: dict[str, Any]) -> str:
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).rstrip()


def render_problem(
    *,
    object_id: str,
    title: str,
    body: str,
    parts: list[str] | None,
    knowledge: list[str] | None,
) -> str:
    front: dict[str, Any] = {
        "schema_version": 1,
        "id": object_id,
        "type": "problem",
        "title": title,
        "status": "draft",
        "created": today(),
        "updated": today(),
    }
    if knowledge:
        front["knowledge"] = knowledge
    if parts:
        front["parts"] = parts
    text = body.strip() or "待填写"
    return f"---\n{dump_front(front)}\n---\n\n# {title}\n\n## 题目\n\n{text}\n"


def render_knowledge(
    *,
    object_id: str,
    title: str,
    body: str,
    domain: str | None,
    aliases: list[str] | None,
) -> str:
    front: dict[str, Any] = {
        "schema_version": 1,
        "id": object_id,
        "type": "knowledge",
        "title": title,
        "status": "draft",
        "created": today(),
        "updated": today(),
    }
    if aliases:
        front["aliases"] = aliases
    if domain:
        front["domain"] = domain
    text = body.strip() or "待填写"
    return f"---\n{dump_front(front)}\n---\n\n# {title}\n\n{text}\n"


def render_method(*, object_id: str, title: str, body: str, knowledge: list[str] | None) -> str:
    front: dict[str, Any] = {
        "schema_version": 1,
        "id": object_id,
        "type": "method",
        "title": title,
        "status": "draft",
    }
    if knowledge:
        front["knowledge"] = knowledge
    text = body.strip() or "待填写"
    return f"---\n{dump_front(front)}\n---\n\n# {title}\n\n{text}\n"
