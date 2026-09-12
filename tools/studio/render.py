"""Reading helpers for Studio S1. Not Frozen Schema."""

from __future__ import annotations

import re
from typing import Any

from tools.problem_validator.parser import extract_front_matter

HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.MULTILINE)
SLUG_RE = re.compile(r"[^\w\u4e00-\u9fff\-、．.]+", re.UNICODE)


def strip_front_matter(text: str) -> str:
    raw, body, _issues = extract_front_matter(text or "")
    return body if raw is not None else (text or "")


def extract_headings(body: str) -> list[dict[str, Any]]:
    source = strip_front_matter(body or "")
    used: dict[str, int] = {}
    headings: list[dict[str, Any]] = []
    for match in HEADING_RE.finditer(source):
        text = re.sub(r"[*_`]", "", match.group(2)).strip()
        headings.append(
            {
                "id": _slug(text, used),
                "level": len(match.group(1)),
                "text": text,
            }
        )
    return headings


def attach_reading(doc: dict[str, Any]) -> dict[str, Any]:
    body = strip_front_matter(doc.get("body") or "")
    doc["body"] = body
    doc["headings"] = extract_headings(body)
    return doc


def _slug(text: str, used: dict[str, int]) -> str:
    cleaned = SLUG_RE.sub("-", text).strip("-")
    if not cleaned:
        cleaned = "section"
    count = used.get(cleaned, 0) + 1
    used[cleaned] = count
    return cleaned if count == 1 else f"{cleaned}-{count}"
