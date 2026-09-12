"""Tool-first tactic baseline and proof-state cache. No Lean model."""

from __future__ import annotations

import json
from pathlib import Path

BASELINE: tuple[str, ...] = ("exact?", "apply?", "simp", "ring", "grind")


def tactic_baseline() -> dict:
    return {
        "order": list(BASELINE),
        "usd": 0.0,
        "model": None,
        "writes_source": False,
        "note": "Declared tool-first order. No specialist Lean model is invoked.",
    }


def cache_proof_state(path: Path, state_hash: str, payload: dict) -> str:
    existing = load_proof_cache(path)
    if any(item.get("state_hash") == state_hash for item in existing):
        return "cached"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"state_hash": state_hash, "payload": payload}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return "recorded"


def load_proof_cache(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
