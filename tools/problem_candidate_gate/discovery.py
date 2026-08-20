"""Project root discovery and Problem Markdown scanning."""

from __future__ import annotations

from pathlib import Path

from .constants import PROBLEM_DIR_NAME, SCHEMA_MARKER_FILE, TEMPLATE_RELATIVE_PATH
from tools.knowledge_validator.constants import KNOWLEDGE_DIR_NAME
from .models import GateIssue, Severity


class DiscoveryError(Exception):
    def __init__(self, message: str, rule_id: str = "PCG-DISC-001") -> None:
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


def problem_dir(project_root: Path) -> Path:
    return project_root / PROBLEM_DIR_NAME


def template_path(project_root: Path) -> Path:
    return (project_root / TEMPLATE_RELATIVE_PATH).resolve()


def is_template_file(path: Path, project_root: Path) -> bool:
    try:
        return path.resolve() == template_path(project_root)
    except OSError:
        return False


def relative_to_root(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def discover_markdown_files(project_root: Path) -> tuple[list[Path], list[Path]]:
    """Recursively find *.md under 02_题目库/. Template excluded by explicit path."""
    base = problem_dir(project_root)
    if not base.is_dir():
        raise DiscoveryError(f"Problem directory not found: {base}")

    included: list[Path] = []
    excluded: list[Path] = []
    for path in sorted(base.rglob("*.md"), key=lambda p: relative_to_root(p, project_root)):
        resolved = path.resolve()
        if is_template_file(path, project_root):
            excluded.append(resolved)
        else:
            included.append(resolved)
    return included, excluded
