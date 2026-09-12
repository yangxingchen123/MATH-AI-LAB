"""Recurring correspondence clusters. Pattern ≠ theorem."""

from __future__ import annotations

from collections import defaultdict

import yaml

from .constants import CORRESPONDENCE_PATH


def pattern_clusters(path=None) -> list[dict]:
    data = yaml.safe_load((path or CORRESPONDENCE_PATH).read_text(encoding="utf-8")) or {}
    theorems = [item for item in (data.get("theorems") or []) if isinstance(item, dict) and item.get("id")]
    by_family: dict[str, list[str]] = defaultdict(list)
    for item in theorems:
        family = str(item.get("family") or "").strip()
        if not family:
            continue
        by_family[family].append(str(item["id"]))
    rows: list[dict] = []
    for family, instances in sorted(by_family.items()):
        if len(instances) < 2:
            continue
        rows.append(
            {
                "id": f"pattern:family:{family}",
                "pattern": (
                    f"Correspondence family '{family}' recurs across {len(instances)} declared lemmas. "
                    "Not a theorem."
                ),
                "kind": "repeated_relationship",
                "instances": instances,
                "confidence": "heuristic",
                "not_a_theorem": True,
            }
        )
    return rows
