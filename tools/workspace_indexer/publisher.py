"""Publish and read generated workspace index files."""

from __future__ import annotations

import os
from pathlib import Path

from .constants import GENERATED_HEADER, INDEX_DIR_RELATIVE, MANAGED_FILES
from .models import IndexerIssue, RenderedWorkspaceIndex


class PublishError(Exception):
    def __init__(self, message: str, rule_id: str = "WI-PUBLISH-001") -> None:
        super().__init__(message)
        self.rule_id = rule_id
        self.message = message


def index_dir_path(project_root: Path) -> Path:
    return project_root / INDEX_DIR_RELATIVE


def is_owned_generated_file(content: str) -> bool:
    return "Generator: tools.workspace_indexer" in content


def read_current_files(project_root: Path) -> dict[str, str] | None:
    index_dir = index_dir_path(project_root)
    if not index_dir.is_dir():
        return None
    out: dict[str, str] = {}
    for name in MANAGED_FILES:
        path = index_dir / name
        if path.is_file():
            out[name] = path.read_text(encoding="utf-8")
    return out if out else None


def list_extra_owned_files(project_root: Path) -> list[str]:
    index_dir = index_dir_path(project_root)
    if not index_dir.is_dir():
        return []
    extra: list[str] = []
    for path in sorted(index_dir.iterdir()):
        if not path.is_file():
            continue
        rel = path.name
        if rel in MANAGED_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if is_owned_generated_file(text):
            extra.append(rel)
    return extra


def publish_index(project_root: Path, rendered: RenderedWorkspaceIndex) -> None:
    index_dir = index_dir_path(project_root)
    index_dir.mkdir(parents=True, exist_ok=True)
    for name in MANAGED_FILES:
        text = rendered.files[name]
        target = index_dir / name
        with target.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)


def compare_to_disk(
    project_root: Path,
    expected: RenderedWorkspaceIndex,
) -> tuple[str, list[IndexerIssue]]:
    from .models import IndexResultKind

    issues: list[IndexerIssue] = []
    index_dir = index_dir_path(project_root)

    if not index_dir.is_dir():
        issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="WI-STALE-001",
                message=f"Generated index directory missing: {INDEX_DIR_RELATIVE}/",
            )
        )
        return IndexResultKind.MISSING.value, issues

    current = read_current_files(project_root) or {}
    for name in MANAGED_FILES:
        if name not in current:
            issues.append(
                IndexerIssue(
                    severity="ERROR",
                    rule_id="WI-STALE-001",
                    message=f"Expected generated file missing: {name}",
                    details={"file": name},
                )
            )
        elif current[name] != expected.files[name]:
            issues.append(
                IndexerIssue(
                    severity="ERROR",
                    rule_id="WI-STALE-002",
                    message=f"Generated file content differs: {name}",
                    details={"file": name},
                )
            )

    for extra in list_extra_owned_files(project_root):
        issues.append(
            IndexerIssue(
                severity="WARNING",
                rule_id="WI-STALE-003",
                message=f"Extra owned generated file: {extra}",
                details={"file": extra},
            )
        )

    if issues:
        if any(i.rule_id == "WI-STALE-001" for i in issues):
            return IndexResultKind.MISSING.value, issues
        return IndexResultKind.STALE.value, issues

    return IndexResultKind.CURRENT.value, issues
