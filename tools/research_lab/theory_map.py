"""Lean modules as theory nodes. No evolution relation is claimed."""

from __future__ import annotations

import yaml

from .constants import CORRESPONDENCE_PATH


def theory_modules(path=None) -> dict:
    data = yaml.safe_load((path or CORRESPONDENCE_PATH).read_text(encoding="utf-8")) or {}
    theorems = [item for item in (data.get("theorems") or []) if isinstance(item, dict) and item.get("lean_file")]
    files: dict[str, list[str]] = {}
    for item in theorems:
        lean_file = str(item["lean_file"])
        files.setdefault(lean_file, []).append(str(item.get("id")))
    nodes = [
        {
            "id": f"theory:{lean_file}",
            "title": lean_file,
            "lemmas": ids,
        }
        for lean_file, ids in sorted(files.items())
    ]
    return {
        "nodes": nodes,
        "edges": [],
        "claims_evolution": False,
        "not_a_theorem": True,
        "note": "One node per Lean module. No extends/simplifies/unifies/specializes is claimed.",
    }
