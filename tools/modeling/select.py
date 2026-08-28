"""Contest-oriented model selection checklist. Not Frozen Schema."""

from __future__ import annotations

REQUIRED_FIELDS: tuple[str, ...] = (
    "name",
    "target_question",
    "why",
    "data_requirement",
    "identifiable_when",
    "falsifiable_when",
)


def rank_model_candidates(candidates: list[dict]) -> list[dict]:
    ranked: list[dict] = []
    for raw in candidates:
        item = dict(raw)
        missing = [key for key in REQUIRED_FIELDS if not str(item.get(key) or "").strip()]
        item["missing"] = missing
        item["eligible"] = not missing and item.get("rejected") is not True
        ranked.append(item)
    ranked.sort(key=lambda row: (not row["eligible"], str(row.get("name") or "")))
    return ranked
