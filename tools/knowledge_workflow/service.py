"""Thin orchestration: resolve target → validate → index."""

from __future__ import annotations

from pathlib import Path

from tools.knowledge_indexer import (
    IndexResultKind,
    build_from_validation,
    check_from_validation,
)
from tools.knowledge_validator import (
    DiscoveryError,
    ValidationIssue,
    ValidationResult,
    focus_view,
    resolve_project_root,
    validate_project,
)
from tools.knowledge_validator.discovery import (
    is_template_file,
    is_under_generated_index,
    knowledge_dir,
    relative_to_root,
)

from .constants import (
    RESULT_FILE_VALIDATION_FAILED,
    RESULT_FULL_VALIDATION_FAILED,
    RESULT_HEALTHY,
    RESULT_INDEX_BUILD_FAILED,
    RESULT_INDEX_MISSING,
    RESULT_INDEX_STALE,
    RESULT_SUCCESS,
    RESULT_SYSTEM_UNHEALTHY,
    RESULT_VALIDATION_FAILED,
    STAGE_FAIL,
    STAGE_PASS,
    STAGE_SKIPPED,
)
from .models import WorkflowIssue, WorkflowResult, WorkflowStageResult


def _skipped(name: str) -> WorkflowStageResult:
    return WorkflowStageResult(name=name, status=STAGE_SKIPPED)


def _from_validator_issue(issue: ValidationIssue) -> WorkflowIssue:
    return WorkflowIssue(
        source="validator",
        severity=issue.severity.value,
        rule_id=issue.rule_id,
        message=issue.message,
        file=issue.file,
        object_id=issue.object_id,
        field=issue.field,
        target_id=issue.target_id,
        details=dict(issue.details),
    )


def _workflow_issue(rule_id: str, message: str, *, file: str | None = None) -> WorkflowIssue:
    return WorkflowIssue(
        source="workflow",
        severity="ERROR",
        rule_id=rule_id,
        message=message,
        file=file,
    )


def _validation_blocked(result: ValidationResult, *, strict_warnings: bool) -> bool:
    if result.summary.errors > 0:
        return True
    return bool(strict_warnings and result.summary.warnings > 0)


def _stage_from_validation(
    name: str,
    result: ValidationResult,
    *,
    strict_warnings: bool,
) -> WorkflowStageResult:
    blocked = _validation_blocked(result, strict_warnings=strict_warnings)
    return WorkflowStageResult(
        name=name,
        status=STAGE_FAIL if blocked else STAGE_PASS,
        errors=result.summary.errors,
        warnings=result.summary.warnings,
        issues=[_from_validator_issue(i) for i in result.issues],
    )


def _empty_result(
    *,
    command: str,
    project_root: str,
    target: str | None,
    strict_warnings: bool,
    result: str,
    file_stage: WorkflowStageResult | None = None,
) -> WorkflowResult:
    stages: dict[str, WorkflowStageResult] = {}
    if command in ("sync", "check"):
        stages["file_validation"] = file_stage or _skipped("file_validation")
        stages["full_validation"] = _skipped("full_validation")
        stages["index"] = _skipped("index")
    else:
        stages["full_validation"] = _skipped("full_validation")
        stages["index_check"] = _skipped("index_check")
    return WorkflowResult(
        result=result,
        project_root=project_root,
        target=target,
        strict_warnings=strict_warnings,
        stages=stages,
        command=command,
    )


def resolve_target(
    path: Path,
    *,
    root: Path | None = None,
) -> tuple[Path, str, WorkflowIssue | None]:
    """
    Resolve a Knowledge Markdown path.

    Returns (project_root, relative_posix, error_or_none).
    """
    try:
        start = path if path.exists() else path.parent
        project_root = resolve_project_root(root, start if start.exists() else None)
    except DiscoveryError as exc:
        return Path.cwd(), str(path), _workflow_issue("KW-ROOT-001", exc.message)

    rel_hint = path.as_posix()
    target = path.expanduser()
    if not target.is_absolute():
        under_root = project_root / path
        if under_root.exists():
            target = under_root.resolve()
        else:
            target = path.resolve()
    else:
        target = target.resolve()

    rel = relative_to_root(target, project_root)

    if not target.exists() or not target.is_file():
        return project_root, rel, _workflow_issue(
            "KW-FILE-002",
            f"Knowledge file does not exist: {rel}",
            file=rel,
        )
    if target.suffix.lower() != ".md":
        return project_root, rel, _workflow_issue(
            "KW-FILE-001",
            f"Workflow target must be a Markdown file (.md): {rel}",
            file=rel,
        )
    if is_template_file(target, project_root):
        return project_root, rel, _workflow_issue(
            "KW-FILE-001",
            "Knowledge template is not a real Knowledge object.",
            file=rel,
        )
    if is_under_generated_index(target, project_root):
        return project_root, rel, _workflow_issue(
            "KW-FILE-001",
            "Generated index files are not Knowledge sources.",
            file=rel,
        )
    try:
        target.resolve().relative_to(knowledge_dir(project_root).resolve())
    except ValueError:
        return project_root, rel, _workflow_issue(
            "KW-FILE-001",
            f"Workflow target must be under 01_知识库/: {rel}",
            file=rel,
        )
    return project_root, rel, None


def _run_validation(project_root: Path) -> ValidationResult:
    return validate_project(root=project_root)


def _index_stage_from_op(op) -> WorkflowStageResult:
    issues = [
        WorkflowIssue(
            source="indexer",
            severity=i.severity,
            rule_id=i.rule_id,
            message=i.message,
            details=dict(i.details),
        )
        for i in op.issues
    ]
    status = op.result.value
    fail = op.result in (IndexResultKind.FAIL, IndexResultKind.STALE, IndexResultKind.MISSING)
    return WorkflowStageResult(
        name="index",
        status=STAGE_FAIL if fail else status,
        errors=1 if fail else 0,
        warnings=0,
        detail=op.result.value,
        issues=issues,
    )


def sync_file(
    path: Path,
    *,
    root: Path | None = None,
    strict_warnings: bool = False,
) -> WorkflowResult:
    project_root, rel, err = resolve_target(path, root=root)
    if err is not None:
        file_stage = WorkflowStageResult(
            name="file_validation",
            status=STAGE_FAIL,
            errors=1,
            issues=[err],
        )
        result_name = (
            RESULT_FILE_VALIDATION_FAILED if err.rule_id.startswith("KW-FILE")
            else RESULT_SYSTEM_UNHEALTHY
        )
        if err.rule_id == "KW-ROOT-001":
            result_name = RESULT_SYSTEM_UNHEALTHY
        return _empty_result(
            command="sync",
            project_root=str(project_root),
            target=rel,
            strict_warnings=strict_warnings,
            result=result_name,
            file_stage=file_stage,
        )

    full = _run_validation(project_root)
    file_view = focus_view(full, (project_root / rel).resolve())

    file_stage = _stage_from_validation("file_validation", file_view, strict_warnings=strict_warnings)
    if file_stage.status == STAGE_FAIL:
        return WorkflowResult(
            result=RESULT_FILE_VALIDATION_FAILED,
            project_root=str(project_root),
            target=rel,
            strict_warnings=strict_warnings,
            stages={
                "file_validation": file_stage,
                "full_validation": _skipped("full_validation"),
                "index": _skipped("index"),
            },
            command="sync",
        )

    full_stage = _stage_from_validation("full_validation", full, strict_warnings=strict_warnings)
    if full_stage.status == STAGE_FAIL:
        return WorkflowResult(
            result=RESULT_FULL_VALIDATION_FAILED,
            project_root=str(project_root),
            target=rel,
            strict_warnings=strict_warnings,
            stages={
                "file_validation": file_stage,
                "full_validation": full_stage,
                "index": _skipped("index"),
            },
            command="sync",
        )

    op = build_from_validation(full, strict_warnings=strict_warnings)
    index_stage = _index_stage_from_op(op)
    if op.result not in (IndexResultKind.BUILT, IndexResultKind.UP_TO_DATE):
        return WorkflowResult(
            result=RESULT_INDEX_BUILD_FAILED,
            project_root=str(project_root),
            target=rel,
            strict_warnings=strict_warnings,
            stages={
                "file_validation": file_stage,
                "full_validation": full_stage,
                "index": index_stage,
            },
            command="sync",
        )

    return WorkflowResult(
        result=RESULT_SUCCESS,
        project_root=str(project_root),
        target=rel,
        strict_warnings=strict_warnings,
        stages={
            "file_validation": file_stage,
            "full_validation": full_stage,
            "index": index_stage,
        },
        command="sync",
    )


def check_file_workflow(
    path: Path,
    *,
    root: Path | None = None,
    strict_warnings: bool = False,
) -> WorkflowResult:
    project_root, rel, err = resolve_target(path, root=root)
    if err is not None:
        file_stage = WorkflowStageResult(
            name="file_validation",
            status=STAGE_FAIL,
            errors=1,
            issues=[err],
        )
        result_name = RESULT_FILE_VALIDATION_FAILED
        if err.rule_id == "KW-ROOT-001":
            result_name = RESULT_SYSTEM_UNHEALTHY
        return _empty_result(
            command="check",
            project_root=str(project_root),
            target=rel,
            strict_warnings=strict_warnings,
            result=result_name,
            file_stage=file_stage,
        )

    full = _run_validation(project_root)
    file_view = focus_view(full, (project_root / rel).resolve())
    file_stage = _stage_from_validation("file_validation", file_view, strict_warnings=strict_warnings)
    if file_stage.status == STAGE_FAIL:
        return WorkflowResult(
            result=RESULT_FILE_VALIDATION_FAILED,
            project_root=str(project_root),
            target=rel,
            strict_warnings=strict_warnings,
            stages={
                "file_validation": file_stage,
                "full_validation": _skipped("full_validation"),
                "index": _skipped("index"),
            },
            command="check",
        )

    full_stage = _stage_from_validation("full_validation", full, strict_warnings=strict_warnings)
    if full_stage.status == STAGE_FAIL:
        return WorkflowResult(
            result=RESULT_FULL_VALIDATION_FAILED,
            project_root=str(project_root),
            target=rel,
            strict_warnings=strict_warnings,
            stages={
                "file_validation": file_stage,
                "full_validation": full_stage,
                "index": _skipped("index"),
            },
            command="check",
        )

    op = check_from_validation(full, strict_warnings=strict_warnings)
    index_stage = _index_stage_from_op(op)
    if op.result == IndexResultKind.CURRENT:
        overall = RESULT_SUCCESS
    elif op.result == IndexResultKind.MISSING:
        overall = RESULT_INDEX_MISSING
    elif op.result == IndexResultKind.STALE:
        overall = RESULT_INDEX_STALE
    else:
        overall = RESULT_INDEX_STALE

    return WorkflowResult(
        result=overall,
        project_root=str(project_root),
        target=rel,
        strict_warnings=strict_warnings,
        stages={
            "file_validation": file_stage,
            "full_validation": full_stage,
            "index": index_stage,
        },
        command="check",
    )


def status(
    *,
    root: Path | None = None,
    strict_warnings: bool = False,
) -> WorkflowResult:
    try:
        project_root = resolve_project_root(root)
    except DiscoveryError as exc:
        return WorkflowResult(
            result=RESULT_SYSTEM_UNHEALTHY,
            project_root=str(root or Path.cwd()),
            target=None,
            strict_warnings=strict_warnings,
            stages={
                "full_validation": WorkflowStageResult(
                    name="full_validation",
                    status=STAGE_FAIL,
                    errors=1,
                    issues=[_workflow_issue("KW-ROOT-001", exc.message)],
                ),
                "index_check": _skipped("index_check"),
            },
            command="status",
        )

    full = _run_validation(project_root)
    full_stage = _stage_from_validation("full_validation", full, strict_warnings=strict_warnings)
    if full_stage.status == STAGE_FAIL:
        return WorkflowResult(
            result=RESULT_VALIDATION_FAILED,
            project_root=str(project_root),
            target=None,
            strict_warnings=strict_warnings,
            stages={
                "full_validation": full_stage,
                "index_check": _skipped("index_check"),
            },
            command="status",
        )

    op = check_from_validation(full, strict_warnings=strict_warnings)
    index_stage = _index_stage_from_op(op)
    index_stage.name = "index_check"
    if op.result == IndexResultKind.CURRENT:
        overall = RESULT_HEALTHY
    elif op.result == IndexResultKind.MISSING:
        overall = RESULT_INDEX_MISSING
    elif op.result == IndexResultKind.STALE:
        overall = RESULT_INDEX_STALE
    else:
        overall = RESULT_INDEX_STALE

    return WorkflowResult(
        result=overall,
        project_root=str(project_root),
        target=None,
        strict_warnings=strict_warnings,
        stages={
            "full_validation": full_stage,
            "index_check": index_stage,
        },
        command="status",
    )
