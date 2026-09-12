"""Append-only failure journal. Rejected candidates are data, not deletions."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_FIELDS: tuple[str, ...] = (
    "problem_id",
    "n",
    "candidate",
    "status",
    "reason",
)


def load_failures(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def append_failure(path: Path, record: dict) -> None:
    missing = [key for key in REQUIRED_FIELDS if key not in record]
    if missing:
        raise ValueError(f"failure record missing {missing}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def lookup_failures(rows: list[dict], query: str) -> list[dict]:
    needle = query.strip().lower()
    if not needle:
        return []
    hits: list[dict] = []
    for row in rows:
        blob = " ".join(str(value) for value in row.values() if value is not None)
        if needle in blob.lower():
            hits.append(row)
    return hits


def as_memory_rows(rows: list[dict]) -> list[dict]:
    """Project journal lines into exploration failure objects. Not Canonical."""
    projected: list[dict] = []
    for index, row in enumerate(rows):
        reason = str(row.get("reason") or row.get("status") or "unknown")
        problem_id = str(row.get("problem_id") or "unknown")
        projected.append(
            {
                "id": f"journal:{problem_id}:{index}",
                "reason": reason,
                "lesson": f"Rejected candidate retained. reason={reason}. Not deleted.",
                "failedAttempt": str(row.get("candidate") or problem_id),
                "source": "failure_journal",
                "not_a_theorem": True,
            }
        )
    return projected
