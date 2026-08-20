"""Project root discovery and Attempt Markdown scanning."""

from __future__ import annotations

import re
from pathlib import Path

from .constants import (
    ATTEMPT_DIR_NAME,
    LEGACY_ATTEMPT_FILENAME_RE,
    LEDGER_FILENAME_RE,
    SCHEMA_MARKER_FILE,
)
from tools.knowledge_validator.constants import KNOWLEDGE_DIR_NAME


class DiscoveryError(Exception):
    def __init__(self, message: str, rule_id: str = "A-DISC-E001") -> None:
        super().__init__(message)
        self.rule_id = rule_id
        self.message = message


def is_project_root(path: Path) -> bool:
    return (path / SCHEMA_MARKER_FILE).is_file() and (path / KNOWLEDGE_DIR_NAME).is_dir()


def find_project_root(start_path: Path | None = None) -> Path:
    current = (start_path or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if is_project_root(candidate):
            return candidate
    raise DiscoveryError(
        f"Cannot find MATH-AI-LAB project root from {current}. "
        f"Expected both '{SCHEMA_MARKER_FILE}' and '{KNOWLEDGE_DIR_NAME}/'."
    )


def resolve_project_root(explicit_root: Path | None = None, start_path: Path | None = None) -> Path:
    if explicit_root is not None:
        root = explicit_root.expanduser().resolve()
        if not is_project_root(root):
            raise DiscoveryError(
                f"Invalid --root: {root}. "
                f"Expected both '{SCHEMA_MARKER_FILE}' and '{KNOWLEDGE_DIR_NAME}/'."
            )
        return root
    return find_project_root(start_path)


def attempt_dir(project_root: Path) -> Path:
    return project_root / ATTEMPT_DIR_NAME


def relative_to_root(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def is_legacy_attempt_filename(name: str) -> bool:
    return re.fullmatch(LEGACY_ATTEMPT_FILENAME_RE, name) is not None


def is_ledger_filename(name: str) -> bool:
    return re.fullmatch(LEDGER_FILENAME_RE, name) is not None


def discover_ledger_files(project_root: Path) -> list[Path]:
    """Find Pxxxx.md ledger files under 11_学习证据/尝试记录/."""
    base = attempt_dir(project_root)
    if not base.is_dir():
        raise DiscoveryError(
            f"Attempt directory not found: {base}",
            rule_id="A-DISC-E003",
        )
    return sorted(
        (
            p.resolve()
            for p in base.glob("*.md")
            if is_ledger_filename(p.name)
        ),
        key=lambda p: relative_to_root(p, project_root),
    )


def discover_legacy_attempt_files(project_root: Path) -> list[Path]:
    """Find legacy Axxxxxx.md files (not allowed in production)."""
    base = attempt_dir(project_root)
    if not base.is_dir():
        return []
    return sorted(
        (
            p.resolve()
            for p in base.glob("*.md")
            if is_legacy_attempt_filename(p.name)
        ),
        key=lambda p: relative_to_root(p, project_root),
    )


def discover_markdown_files(project_root: Path) -> list[Path]:
    """Find production Attempt ledger files under 11_学习证据/尝试记录/."""
    return discover_ledger_files(project_root)
