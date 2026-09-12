"""Task object schema from the original lab design §7.3. Not Frozen Schema."""

from __future__ import annotations

from pathlib import Path

import yaml

REQUIRED: tuple[str, ...] = (
    "task_id",
    "problem_id",
    "stage",
    "input_hash",
    "budget",
    "result",
    "cost",
)


def load_task(path: Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("task must be a mapping")
    return data


def validate_task(data: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED:
        if not data.get(key):
            errors.append(f"missing {key}")
    budget = data.get("budget")
    if isinstance(budget, dict):
        if "hard_limit_usd" not in budget or "hard_limit_seconds" not in budget:
            errors.append("budget needs hard_limit_usd and hard_limit_seconds")
    elif budget:
        errors.append("budget must be a mapping")
    cost = data.get("cost")
    if isinstance(cost, dict) and float(cost.get("usd") or 0) < 0:
        errors.append("cost.usd must be non-negative")
    result = data.get("result")
    if isinstance(result, dict) and not result.get("verifier"):
        errors.append("result.verifier required")
    model = data.get("model")
    if model is not None and not isinstance(model, dict):
        errors.append("model must be a mapping")
    return errors
