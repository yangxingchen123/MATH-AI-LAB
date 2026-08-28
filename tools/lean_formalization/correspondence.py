"""Natural-language ↔ Lean statement correspondence."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .models import CorrespondenceResult

REQUIRED_KEYS = ("id", "natural_language", "lean_decl", "lean_file", "family")
THEOREM_RE = re.compile(r"^theorem\s+(\w+)", re.MULTILINE)


def load_table(path: Path) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    entries = data.get("theorems")
    if not isinstance(entries, list):
        raise ValueError("correspondence.yaml must have theorems: []")
    return entries


def validate_table(entries: list[dict], project_root: Path) -> CorrespondenceResult:
    errors: list[str] = []
    families: set[str] = set()
    root = Path(project_root)
    for item in entries:
        for key in REQUIRED_KEYS:
            if not item.get(key):
                errors.append(f"missing {key} in {item!r}")
        lean_file = root / str(item.get("lean_file", ""))
        if item.get("lean_file") and not lean_file.is_file():
            errors.append(f"missing lean file: {item.get('lean_file')}")
        elif lean_file.is_file() and item.get("lean_decl"):
            text = lean_file.read_text(encoding="utf-8")
            decl = str(item["lean_decl"]).rsplit(".", 1)[-1]
            if f"theorem {decl}" not in text and f"def {decl}" not in text:
                errors.append(f"declaration {decl} not found in {item['lean_file']}")
        nl_ref = item.get("natural_language_ref")
        if nl_ref and not (root / str(nl_ref)).is_file():
            errors.append(f"missing natural_language_ref: {nl_ref}")
        if item.get("family"):
            families.add(str(item["family"]))
    if len(families) < 2:
        errors.append("need at least two distinct proposition families")
    return CorrespondenceResult(ok=not errors, errors=errors, families=sorted(families))


def undeclared_theorems(project_root: Path, entries: list[dict]) -> list[str]:
    listed = {str(item.get("lean_decl") or "").rsplit(".", 1)[-1] for item in entries}
    missing: list[str] = []
    for path in sorted(Path(project_root).rglob("*.lean")):
        text = path.read_text(encoding="utf-8")
        for name in THEOREM_RE.findall(text):
            if name not in listed:
                missing.append(name)
    return missing
