"""Literature, NL↔Lean template, recipes, papers, experts, holdout, inventory sidecar."""

from __future__ import annotations

from pathlib import Path

import yaml

from .constants import (
    CORRESPONDENCE_PATH,
    EXPERTS_DIR,
    HOLDOUT_PATH,
    LITERATURE_DIR,
    PAPERS_DIR,
)
from .inventory import FORBIDDEN_WRITE_NAMES, scan_inventory

NL_LEAN_FIELDS: tuple[str, ...] = (
    "id",
    "natural_language",
    "lean_decl",
    "lean_file",
    "family",
)
LIT_REQUIRED: tuple[str, ...] = ("id", "title", "version", "locator")


def list_yaml(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(root.glob("*.yaml"))


def validate_literature(data: dict) -> list[str]:
    errors: list[str] = []
    for key in LIT_REQUIRED:
        if not data.get(key):
            errors.append(f"missing {key}")
    if data.get("doi") is None and data.get("arxiv") is None and not data.get("locator"):
        errors.append("doi/arxiv/locator required")
    return errors


def load_all_literature() -> list[dict]:
    rows: list[dict] = []
    for path in list_yaml(LITERATURE_DIR):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        data["_path"] = str(path)
        rows.append(data)
    return rows


def review_nl_lean(path: Path | None = None) -> dict:
    target = path or CORRESPONDENCE_PATH
    data = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    theorems = data.get("theorems") or []
    missing: list[str] = []
    for item in theorems:
        if not isinstance(item, dict):
            missing.append("non-mapping theorem")
            continue
        for key in NL_LEAN_FIELDS:
            if not item.get(key):
                missing.append(f"{item.get('id')}:{key}")
    return {
        "ok": missing == [],
        "count": len(theorems),
        "missing": missing,
        "writes_source": False,
        "template": "natural_language ↔ lean_decl",
    }


def reproduction_recipe() -> dict:
    return {
        "python": "3.13",
        "lockfile": "requirements.lock",
        "lean": "4.15.0",
        "mathlib": "none",
        "commands": [
            "python -m tools.research_lab operate",
            "python -m tools.research_lab cycle --n 5",
            "python -m tools.research_lab funnel --n 5 --limit 8",
            "python -m tools.research_lab journal",
        ],
        "container": False,
        "writes_source": False,
        "note": "Local recipe, not an independent Docker container.",
    }


def paper_checklists() -> dict:
    rows: list[dict] = []
    for path in list_yaml(PAPERS_DIR):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows.append(data)
    kinds = {item.get("kind") for item in rows}
    return {
        "ok": {"math", "system"} <= kinds
        and all(item.get("claims_四大") is False for item in rows)
        and all(item.get("filled") is False for item in rows),
        "drafts": rows,
        "filled": False,
        "claims_四大": False,
        "writes_source": False,
    }


def load_experts() -> list[dict]:
    rows: list[dict] = []
    for path in list_yaml(EXPERTS_DIR):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows.append(data)
    return rows


def experts_ok() -> bool:
    rows = load_experts()
    if not rows:
        return False
    return all(item.get("signoff") is False for item in rows) and any(
        "second_external" in item for item in rows
    )


def load_holdout() -> dict:
    data = yaml.safe_load(HOLDOUT_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("holdout must be a mapping")
    return data


def render_inventory_sidecar(report: dict) -> str:
    present = ", ".join(report.get("present") or [])
    missing = ", ".join(report.get("missing") or []) or "none"
    return (
        "# Derived inventory sidecar\n\n"
        "This file is generated from a warehouse scan. It is **not** "
        "`09_长期记忆/项目进度.md` and does not record project judgment.\n\n"
        f"- root: `{report.get('root')}`\n"
        f"- file_total: {report.get('file_total')}\n"
        f"- present: {present}\n"
        f"- missing: {missing}\n"
    )


def write_sidecar(path: Path, report: dict | None = None) -> None:
    target = Path(path)
    if target.name in FORBIDDEN_WRITE_NAMES:
        raise ValueError(f"refusing to write {target.name}")
    payload = report if report is not None else scan_inventory()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_inventory_sidecar(payload), encoding="utf-8")
