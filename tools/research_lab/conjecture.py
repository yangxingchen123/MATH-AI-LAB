"""Conjecture + prior-art records. Candidate contract, not Frozen Schema."""

from __future__ import annotations

from pathlib import Path

import yaml

from .constants import CONJECTURES_DIR
from .registry import (
    PRIOR_ART_RELATIONS,
    STAGES,
    TERMINAL_STAGES,
    load_record,
    validate_prior_art,
)

RELATIONS = PRIOR_ART_RELATIONS

REQUIRED_FIELDS: tuple[str, ...] = ("id", "problem_id", "statement", "status")


def list_conjecture_paths(root: Path | None = None) -> list[Path]:
    base = Path(root) if root is not None else CONJECTURES_DIR
    if not base.is_dir():
        return []
    return sorted(base.glob("*.yaml"))


def load_conjecture(path: Path) -> dict:
    return load_record(path)


def validate_conjecture(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["conjecture must be a mapping"]
    for key in REQUIRED_FIELDS:
        if not data.get(key):
            errors.append(f"missing {key}")
    status = data.get("status")
    allowed = set(STAGES) | set(TERMINAL_STAGES)
    if status and status not in allowed:
        errors.append(f"unknown status: {status}")
    if data.get("novelty_claim") == "first" and not data.get("expert_signoff"):
        errors.append("novelty_claim=first requires expert_signoff")
    claim = data.get("novelty_claim")
    if claim in {"known", "first"}:
        errors.extend(validate_prior_art(data.get("prior_art"), required=True))
    elif data.get("prior_art") is not None:
        errors.extend(validate_prior_art(data.get("prior_art"), required=False))
    return errors


def load_all_conjectures(root: Path | None = None) -> list[dict]:
    rows: list[dict] = []
    for path in list_conjecture_paths(root):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        data["_path"] = str(path)
        rows.append(data)
    return rows
