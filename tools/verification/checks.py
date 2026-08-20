"""Adapt existing validators / checks into VerificationCheckResult."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from tools.attempt_validator import validate_project as validate_attempt_project
from tools.knowledge_validator import validate_project as validate_knowledge_project
from tools.latex_build import check_latex_project
from tools.latex_build.resolver import LatexBuildError
from tools.method_validator import validate_project as validate_method_project
from tools.problem_validator import validate_project as validate_problem_project
from tools.workspace_check import run_workspace_check
from tools.workspace_indexer import check_index
from tools.workspace_indexer.models import IndexResultKind

from .models import FailureCategory, VerificationCheckResult, VerificationStatus

SOURCE_ACTION = "Fix the reported Source validation errors, then rerun verification."
STALE_ACTION = "python -m tools.workspace_indexer sync"
TOOLCHAIN_ACTION = "Install/configure the canonical XeLaTeX toolchain."
LATEX_ACTION = "Fix the reported LaTeX compile/inspection errors, then rerun latex-smoke."
TEST_ACTION = "Fix the failing tests, then rerun verification."


def _timed() -> float:
    return time.perf_counter()


def _from_validator(
    *,
    name: str,
    result,
    duration: float,
) -> VerificationCheckResult:
    errors = int(getattr(result.summary, "errors", 0) or 0)
    warnings = int(getattr(result.summary, "warnings", 0) or 0)
    details = "; ".join(
        f"[{getattr(i, 'rule_id', '')}] {getattr(i, 'message', '')}"
        for i in list(getattr(result, "issues", []))[:8]
    )
    if errors:
        return VerificationCheckResult(
            name=name,
            status=VerificationStatus.FAIL,
            category=FailureCategory.SOURCE_INVALID,
            summary=f"{name} reported {errors} error(s).",
            details=details,
            duration_seconds=duration,
            suggested_action=SOURCE_ACTION,
            layer="SOURCE INTEGRITY",
        )
    if warnings:
        return VerificationCheckResult(
            name=name,
            status=VerificationStatus.PASS_WITH_WARNINGS,
            summary=f"{name} passed with {warnings} warning(s).",
            details=details,
            duration_seconds=duration,
            layer="SOURCE INTEGRITY",
        )
    return VerificationCheckResult(
        name=name,
        status=VerificationStatus.PASS,
        summary=f"{name} passed.",
        duration_seconds=duration,
        layer="SOURCE INTEGRITY",
    )


def run_knowledge_validator(root: Path) -> tuple[VerificationCheckResult, object]:
    start = _timed()
    result = validate_knowledge_project(root=root)
    return _from_validator(name="Knowledge Validator", result=result, duration=_timed() - start), result


def run_problem_validator(root: Path, knowledge_result=None) -> tuple[VerificationCheckResult, object]:
    start = _timed()
    result = validate_problem_project(root=root, knowledge_result=knowledge_result)
    return _from_validator(name="Problem Validator", result=result, duration=_timed() - start), result


def run_attempt_validator(root: Path, problem_result=None) -> tuple[VerificationCheckResult, object]:
    start = _timed()
    result = validate_attempt_project(root=root, problem_result=problem_result)
    return _from_validator(name="Attempt Validator", result=result, duration=_timed() - start), result


def run_method_validator(root: Path, knowledge_result=None) -> tuple[VerificationCheckResult, object]:
    start = _timed()
    result = validate_method_project(root=root, knowledge_result=knowledge_result)
    return _from_validator(name="Method Validator", result=result, duration=_timed() - start), result


def blocked_derived(name: str) -> VerificationCheckResult:
    return VerificationCheckResult(
        name=name,
        status=VerificationStatus.BLOCKED,
        category=FailureCategory.SOURCE_INVALID,
        summary="Source validation is not trustworthy; derived integrity was not executed.",
        suggested_action=SOURCE_ACTION,
        layer="DERIVED INTEGRITY",
    )


def run_workspace_indexer_check(root: Path) -> VerificationCheckResult:
    start = _timed()
    op = check_index(root=root)
    duration = _timed() - start
    details = "; ".join(f"[{i.rule_id}] {i.message}" for i in op.issues[:8])
    if op.result in (IndexResultKind.CURRENT, IndexResultKind.UP_TO_DATE, IndexResultKind.BUILT):
        return VerificationCheckResult(
            name="Workspace Indexer",
            status=VerificationStatus.PASS,
            summary="Generated views are current.",
            duration_seconds=duration,
            layer="DERIVED INTEGRITY",
        )
    if op.result in (IndexResultKind.STALE, IndexResultKind.MISSING):
        return VerificationCheckResult(
            name="Workspace Indexer",
            status=VerificationStatus.FAIL,
            category=FailureCategory.GENERATED_STALE,
            summary="Generated files are stale or missing.",
            details=details,
            duration_seconds=duration,
            suggested_action=STALE_ACTION,
            layer="DERIVED INTEGRITY",
        )
    return VerificationCheckResult(
        name="Workspace Indexer",
        status=VerificationStatus.FAIL,
        category=FailureCategory.WORKSPACE_INVALID,
        summary="Workspace Indexer check failed.",
        details=details,
        duration_seconds=duration,
        suggested_action=SOURCE_ACTION,
        layer="DERIVED INTEGRITY",
    )


def run_workspace_check_adapter(root: Path) -> VerificationCheckResult:
    start = _timed()
    result = run_workspace_check(root=root)
    duration = _timed() - start
    details = "; ".join(f"[{i.rule_id}] {i.message}" for i in result.issues[:8])
    stale = any(i.rule_id == "WC007" for i in result.issues)
    if result.error_count > 0:
        category = FailureCategory.GENERATED_STALE if stale else FailureCategory.WORKSPACE_INVALID
        action = STALE_ACTION if category == FailureCategory.GENERATED_STALE else SOURCE_ACTION
        return VerificationCheckResult(
            name="Workspace Check",
            status=VerificationStatus.FAIL,
            category=category,
            summary=f"Workspace Check reported {result.error_count} error(s).",
            details=details,
            duration_seconds=duration,
            suggested_action=action,
            layer="DERIVED INTEGRITY",
        )
    if result.warning_count > 0:
        return VerificationCheckResult(
            name="Workspace Check",
            status=VerificationStatus.PASS_WITH_WARNINGS,
            summary=f"Workspace Check passed with {result.warning_count} warning(s).",
            details=details,
            duration_seconds=duration,
            layer="DERIVED INTEGRITY",
        )
    return VerificationCheckResult(
        name="Workspace Check",
        status=VerificationStatus.PASS,
        summary="Workspace Check passed.",
        duration_seconds=duration,
        layer="DERIVED INTEGRITY",
    )


def default_pytest_runner(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def run_pytest_check(
    root: Path,
    *,
    pytest_runner: Callable[[Path], subprocess.CompletedProcess[str]] | None = None,
) -> VerificationCheckResult:
    start = _timed()
    runner = pytest_runner or default_pytest_runner
    completed = runner(root)
    duration = _timed() - start
    output = (completed.stdout or "") + (completed.stderr or "")
    snippet = "\n".join(output.strip().splitlines()[-20:])
    if completed.returncode == 0:
        return VerificationCheckResult(
            name="pytest",
            status=VerificationStatus.PASS,
            summary="pytest passed.",
            details=snippet,
            duration_seconds=duration,
            layer="SOFTWARE INTEGRITY",
        )
    return VerificationCheckResult(
        name="pytest",
        status=VerificationStatus.FAIL,
        category=FailureCategory.TEST_FAILURE,
        summary=f"pytest failed (exit {completed.returncode}).",
        details=snippet,
        duration_seconds=duration,
        suggested_action=TEST_ACTION,
        layer="SOFTWARE INTEGRITY",
    )


def run_latex_smoke(
    root: Path,
    project: str,
    *,
    check_fn: Callable[..., object] | None = None,
) -> VerificationCheckResult:
    start = _timed()
    checker = check_fn or check_latex_project
    try:
        result = checker(project, repo_root=root)
    except LatexBuildError as exc:
        return VerificationCheckResult(
            name="LaTeX Smoke",
            status=VerificationStatus.FAIL,
            category=FailureCategory.LATEX_FAILURE,
            summary=str(exc),
            duration_seconds=_timed() - start,
            suggested_action=LATEX_ACTION,
            layer="ARTIFACT INTEGRITY",
        )
    duration = _timed() - start
    compile_issues = tuple(getattr(result.compile_result, "issues", ()) or ())
    if any(getattr(issue, "code", "") == "TOOLCHAIN_MISSING" for issue in compile_issues):
        return VerificationCheckResult(
            name="LaTeX Smoke",
            status=VerificationStatus.BLOCKED,
            category=FailureCategory.TOOLCHAIN_MISSING,
            summary="xelatex executable not found.",
            duration_seconds=duration,
            suggested_action=TOOLCHAIN_ACTION,
            layer="ARTIFACT INTEGRITY",
        )
    if not result.inspection_result.publish_allowed or not result.compile_result.success:
        details = "; ".join(
            f"[{i.code}] {i.message}" for i in result.inspection_result.blocking_errors[:8]
        )
        return VerificationCheckResult(
            name="LaTeX Smoke",
            status=VerificationStatus.FAIL,
            category=FailureCategory.LATEX_FAILURE,
            summary="LaTeX smoke check failed.",
            details=details,
            duration_seconds=duration,
            suggested_action=LATEX_ACTION,
            layer="ARTIFACT INTEGRITY",
        )
    if result.warning_count:
        details = "; ".join(
            f"[{i.code}] {i.message}" for i in result.inspection_result.warnings[:5]
        )
        return VerificationCheckResult(
            name="LaTeX Smoke",
            status=VerificationStatus.PASS_WITH_WARNINGS,
            summary=f"LaTeX smoke passed with {result.warning_count} warning(s).",
            details=details,
            duration_seconds=duration,
            layer="ARTIFACT INTEGRITY",
        )
    return VerificationCheckResult(
        name="LaTeX Smoke",
        status=VerificationStatus.PASS,
        summary="LaTeX smoke check passed.",
        duration_seconds=duration,
        layer="ARTIFACT INTEGRITY",
    )


def collect_environment(root: Path, *, latex_project: str | None = None) -> dict[str, str]:
    env = {
        "Python": sys.version.split()[0],
        "Platform": sys.platform,
        "Repository Root": str(root),
    }
    if latex_project:
        env["Smoke project"] = latex_project
        xelatex = shutil.which("xelatex")
        env["XeLaTeX path"] = xelatex or "(not found)"
        if xelatex:
            try:
                proc = subprocess.run(
                    [xelatex, "--version"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                first = (proc.stdout or proc.stderr or "").splitlines()
                env["XeLaTeX version"] = first[0] if first else "unknown"
            except OSError:
                env["XeLaTeX version"] = "unknown"
    return env


@dataclass
class CheckHooks:
    """Injectable adapters. Production defaults never include sync / rebuild / publish."""

    knowledge: Callable[[Path], tuple[VerificationCheckResult, object]] | None = None
    problem: Callable[..., tuple[VerificationCheckResult, object]] | None = None
    attempt: Callable[..., tuple[VerificationCheckResult, object]] | None = None
    method: Callable[..., tuple[VerificationCheckResult, object]] | None = None
    workspace_indexer: Callable[[Path], VerificationCheckResult] | None = None
    workspace_check: Callable[[Path], VerificationCheckResult] | None = None
    pytest: Callable[[Path], VerificationCheckResult] | None = None
    latex: Callable[[Path, str], VerificationCheckResult] | None = None
    forbidden_calls: list[str] = field(default_factory=list)
