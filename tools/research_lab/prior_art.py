"""Prior-art relation matrix. Theorem-level relations, not title similarity."""

from __future__ import annotations

from .conjecture import load_all_conjectures
from .constants import PROBLEMS_DIR
from .registry import PRIOR_ART_RELATIONS, list_problem_paths, load_record


def build_matrix() -> dict:
    rows: list[dict] = []
    counts = {name: 0 for name in PRIOR_ART_RELATIONS}
    for path in list_problem_paths(PROBLEMS_DIR):
        _collect(load_record(path), rows, counts)
    for item in load_all_conjectures():
        _collect(item, rows, counts)
    return {
        "ok": bool(rows),
        "writes_source": False,
        "core_impact": False,
        "counts": counts,
        "rows": rows,
        "note": "Relations are candidate labels. Novelty is not decided by this matrix.",
    }


def _collect(record: dict, rows: list[dict], counts: dict[str, int]) -> None:
    for entry in record.get("prior_art") or []:
        if not isinstance(entry, dict):
            continue
        relation = str(entry.get("relation") or "")
        if relation in counts:
            counts[relation] += 1
        rows.append(
            {
                "id": record.get("id"),
                "problem_id": record.get("problem_id") or record.get("id"),
                "relation": relation,
                "note": entry.get("note"),
            }
        )
