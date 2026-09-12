"""Allocate next Frozen IDs from the repository. UI must not guess IDs."""

from __future__ import annotations

import re
from pathlib import Path

from tools.knowledge_validator.constants import ID_PATTERN as K_PATTERN
from tools.knowledge_validator.constants import RESERVED_ID as K_RESERVED
from tools.method_validator.constants import ID_PATTERN as M_PATTERN
from tools.method_validator.constants import RESERVED_METHOD_ID
from tools.problem_validator.constants import ID_PATTERN as P_PATTERN
from tools.problem_validator.constants import RESERVED_PROBLEM_ID

ID_LINE = re.compile(r"^id:\s*([A-Z]\d{4})\s*$", re.MULTILINE)


def _collect(root: Path, directory: str, pattern: str, reserved: str) -> list[str]:
    base = root / directory
    found: list[str] = []
    if not base.is_dir():
        return found
    compiled = re.compile(pattern)
    for path in base.rglob("*.md"):
        rel = path.relative_to(root).as_posix()
        if "/_索引/" in f"/{rel}/" or path.name.endswith("模板.md"):
            continue
        text = path.read_text(encoding="utf-8")
        match = ID_LINE.search(text)
        if not match:
            continue
        object_id = match.group(1)
        if object_id == reserved or not compiled.fullmatch(object_id):
            continue
        found.append(object_id)
    return found


def existing_problem_ids(root: Path) -> list[str]:
    return _collect(root, "02_题目库", P_PATTERN, RESERVED_PROBLEM_ID)


def existing_knowledge_ids(root: Path) -> list[str]:
    return _collect(root, "01_知识库", K_PATTERN, K_RESERVED)


def existing_method_ids(root: Path) -> list[str]:
    return _collect(root, "12_方法库", M_PATTERN, RESERVED_METHOD_ID)


def next_id(existing: list[str], prefix: str) -> str:
    used = {int(item[1:]) for item in existing if item.startswith(prefix)}
    n = max(used) + 1 if used else 1
    return f"{prefix}{n:04d}"


def allocate_problem_id(root: Path) -> str:
    return next_id(existing_problem_ids(root), "P")


def allocate_knowledge_id(root: Path) -> str:
    return next_id(existing_knowledge_ids(root), "K")


def allocate_method_id(root: Path) -> str:
    return next_id(existing_method_ids(root), "M")
