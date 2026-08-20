"""Staleness detection without modifying files."""

from __future__ import annotations

from pathlib import Path

from .constants import MANAGED_FILES
from .models import IndexResultKind, IndexerIssue, RenderedIndex
from .publisher import index_dir_path, list_unexpected_files, read_current_index_files


def compare_to_expected(
    project_root: Path,
    expected: RenderedIndex,
) -> tuple[IndexResultKind, list[IndexerIssue]]:
    index_dir = index_dir_path(project_root)
    issues: list[IndexerIssue] = []

    if not index_dir.exists():
        issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-STALE-001",
                message="Index directory missing: 01_知识库/_索引/",
            )
        )
        return IndexResultKind.MISSING, issues

    unexpected = list_unexpected_files(project_root)
    for name in unexpected:
        issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-STALE-003",
                message=f"Unexpected file in generated index directory: {name}",
                details={"file": name},
            )
        )

    current = read_current_index_files(project_root) or {}
    for name in MANAGED_FILES:
        if name not in current:
            issues.append(
                IndexerIssue(
                    severity="ERROR",
                    rule_id="KI-STALE-001",
                    message=f"Expected generated file missing: {name}",
                    details={"file": name},
                )
            )
        elif current[name] != expected.files[name]:
            issues.append(
                IndexerIssue(
                    severity="ERROR",
                    rule_id="KI-STALE-002",
                    message=f"Generated file content differs: {name}",
                    details={"file": name},
                )
            )

    if issues:
        # Missing vs stale: if dir missing already returned; else STALE
        if not any(i.rule_id == "KI-STALE-001" and "Index directory missing" in i.message for i in issues):
            return IndexResultKind.STALE, issues
        # Some managed files missing
        return IndexResultKind.STALE, issues

    return IndexResultKind.CURRENT, issues
