"""Read-only workspace consistency checker."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from tools.attempt_validator import validate_project as validate_attempt_project
from tools.knowledge_validator import resolve_project_root, validate_project as validate_knowledge_project
from tools.knowledge_validator.discovery import DiscoveryError
from tools.method_validator import validate_project as validate_method_project
from tools.problem_validator import validate_project as validate_problem_project
from tools.workspace_indexer.builder import build_workspace_snapshot
from tools.workspace_indexer.constants import MANAGED_FILES
from tools.workspace_indexer.models import RenderedWorkspaceIndex
from tools.workspace_indexer.publisher import compare_to_disk
from tools.workspace_indexer.renderer import render_all

GOVERNANCE_DOCS: tuple[str, ...] = (
    "项目规则.md",
    "AGENTS.md",
    "元数据规范.md",
    "学习证据架构.md",
    "09_长期记忆/项目进度.md",
)

MOVABLE_PATH_PATTERN = re.compile(
    r"02_题目库/(?:未解决|研究中|已解决)/P\d{4}[^\s`\"]+\.md"
)


@dataclass
class CheckIssue:
    severity: str
    rule_id: str
    message: str


@dataclass
class WorkspaceCheckResult:
    project_root: str
    knowledge_validation: str = "UNKNOWN"
    problem_validation: str = "UNKNOWN"
    attempt_validation: str = "UNKNOWN"
    method_validation: str = "UNKNOWN"
    knowledge_errors: int = 0
    problem_errors: int = 0
    attempt_errors: int = 0
    method_errors: int = 0
    knowledge_warnings: int = 0
    problem_warnings: int = 0
    attempt_warnings: int = 0
    method_warnings: int = 0
    repository_facts: dict[str, object] = field(default_factory=dict)
    generated_status: dict[str, str] = field(default_factory=dict)
    issues: list[CheckIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "WARNING")


def _scan_movable_path_references(project_root: Path) -> list[CheckIssue]:
    issues: list[CheckIssue] = []
    for rel in GOVERNANCE_DOCS:
        path = project_root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in MOVABLE_PATH_PATTERN.finditer(text):
            issues.append(
                CheckIssue(
                    severity="WARNING",
                    rule_id="WC-MOVABLE-W001",
                    message=(
                        f"Movable Problem path used as reference in {rel}: {match.group(0)}"
                    ),
                )
            )
    return issues


def _generated_file_status(
    project_root: Path,
    expected: RenderedWorkspaceIndex,
) -> dict[str, str]:
    from tools.workspace_indexer.publisher import read_current_files

    current = read_current_files(project_root)
    status: dict[str, str] = {}
    for name in MANAGED_FILES:
        if current is None or name not in current:
            status[name] = "MISSING"
        elif current[name] != expected.files[name]:
            status[name] = "STALE"
        else:
            status[name] = "CURRENT"
    return status


def run_workspace_check(*, root: Path | None = None) -> WorkspaceCheckResult:
    try:
        project_root = resolve_project_root(root)
    except DiscoveryError as exc:
        return WorkspaceCheckResult(
            project_root=str(root or Path.cwd()),
            issues=[CheckIssue("ERROR", "WC-ROOT-E001", exc.message)],
        )

    result = WorkspaceCheckResult(project_root=str(project_root))

    knowledge_result = validate_knowledge_project(root=project_root)
    result.knowledge_validation = knowledge_result.summary.result
    result.knowledge_errors = knowledge_result.summary.errors
    result.knowledge_warnings = knowledge_result.summary.warnings
    if knowledge_result.summary.errors > 0:
        result.issues.append(
            CheckIssue("ERROR", "WC001", "Knowledge validation failed.")
        )

    problem_result = validate_problem_project(root=project_root, knowledge_result=knowledge_result)
    result.problem_validation = problem_result.summary.result
    result.problem_errors = problem_result.summary.errors
    result.problem_warnings = problem_result.summary.warnings
    if problem_result.summary.errors > 0:
        result.issues.append(
            CheckIssue("ERROR", "WC002", "Problem validation failed.")
        )

    attempt_result = validate_attempt_project(root=project_root, problem_result=problem_result)
    result.attempt_validation = attempt_result.summary.result
    result.attempt_errors = attempt_result.summary.errors
    result.attempt_warnings = attempt_result.summary.warnings
    if attempt_result.summary.errors > 0:
        result.issues.append(
            CheckIssue("ERROR", "WC003", "Attempt validation failed.")
        )

    method_result = validate_method_project(root=project_root, knowledge_result=knowledge_result)
    result.method_validation = method_result.summary.result
    result.method_errors = method_result.summary.errors
    result.method_warnings = method_result.summary.warnings
    if method_result.summary.errors > 0:
        result.issues.append(
            CheckIssue("ERROR", "WC004", "Method validation failed.")
        )

    if (
        knowledge_result.summary.errors == 0
        and problem_result.summary.errors == 0
        and attempt_result.summary.errors == 0
        and method_result.summary.errors == 0
    ):
        snapshot = build_workspace_snapshot(
            project_root,
            knowledge_result=knowledge_result,
            problem_result=problem_result,
            attempt_result=attempt_result,
            method_result=method_result,
        )
        result.repository_facts = {
            "knowledge_entries": len(snapshot.knowledge_rows),
            "problems": len(snapshot.problem_rows),
            "attempts": len(snapshot.attempt_rows),
            "methods": len(snapshot.method_rows),
            "workflow_counts": dict(snapshot.problem_workflow_counts),
            "published_pdfs": snapshot.pdf_count,
            "latex_projects": snapshot.latex_project_count,
        }

        expected = RenderedWorkspaceIndex(files=render_all(snapshot))
        result.generated_status = _generated_file_status(project_root, expected)
        kind, stale_issues = compare_to_disk(project_root, expected)
        for si in stale_issues:
            result.issues.append(CheckIssue(si.severity, "WC007", si.message))
        if kind != "CURRENT":
            result.issues.append(
                CheckIssue(
                    "WARNING" if kind == "STALE" else "ERROR",
                    "WC007",
                    f"Generated views status: {kind}",
                )
            )

    result.issues.extend(_scan_movable_path_references(project_root))
    return result
