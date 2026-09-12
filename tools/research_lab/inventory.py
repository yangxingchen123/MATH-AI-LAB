"""Read-only warehouse inventory. Does not write 09_长期记忆/项目进度.md."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .constants import KEY_ROOTS, SKIP_DIR_NAMES

FORBIDDEN_WRITE_NAMES: frozenset[str] = frozenset(
    {"项目进度.md", "元数据规范.md", "AGENTS.md", "项目规则.md"}
)


def scan_inventory(root: Path | None = None) -> dict:
    base = Path(root) if root is not None else Path.cwd()
    counts: Counter[str] = Counter()
    missing: list[str] = []
    present: list[str] = []
    for rel in KEY_ROOTS:
        path = base / rel
        if not path.exists():
            missing.append(rel)
            continue
        present.append(rel)
        if path.is_file():
            counts[path.suffix or path.name] += 1
            continue
        for item in path.rglob("*"):
            if any(part in SKIP_DIR_NAMES for part in item.parts):
                continue
            if item.is_file():
                counts[item.suffix.lower() or item.name] += 1
    return {
        "root": str(base),
        "present": present,
        "missing": missing,
        "file_counts_by_suffix": dict(sorted(counts.items())),
        "file_total": int(sum(counts.values())),
        "key_roots_complete": not missing,
    }


def write_inventory(report: dict, path: Path) -> None:
    target = Path(path)
    if target.name in FORBIDDEN_WRITE_NAMES:
        raise ValueError(f"refusing to write {target.name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

