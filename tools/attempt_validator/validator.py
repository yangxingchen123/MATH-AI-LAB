"""Orchestration: Problem dependency → discover → parse → validate → registry."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from tools.problem_validator.models import ProblemDocument, ValidationResult as ProblemValidationResult
from tools.problem_validator.validator import validate_project as validate_problem_project

from .discovery import (
    DiscoveryError,
    discover_legacy_attempt_files,
    discover_markdown_files,
    relative_to_root,
    resolve_project_root,
)
from .ledger import (
    expand_ledger_to_documents,
    load_ledger_file,
    validate_ledger_container,
)
from .models import (
    AttemptDocument,
    DependencySummary,
    Severity,
    ValidationIssue,
    ValidationResult,
    ValidationSummary,
)
from .rules_object import (
    validate_base,
    validate_part_shape,
    validate_problem_relation,
    validate_unique_ids,
)

_load_ledger_file: Callable[..., object] = load_ledger_file


def set_load_ledger_file_for_tests(fn: Callable[..., object] | None) -> None:
    global _load_ledger_file
    _load_ledger_file = fn or load_ledger_file


def _resolve_problem(
    project_root: Path,
    problem_result: ProblemValidationResult | None,
) -> tuple[ProblemValidationResult, bool, dict[str, ProblemDocument], list[ValidationIssue]]:
    if problem_result is None:
        problem_result = validate_problem_project(root=project_root)

    issues: list[ValidationIssue] = []
    healthy = problem_result.summary.errors == 0
    if not healthy:
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="A-PROB-E010",
                message=(
                    "Problem dependency validation failed; "
                    "Attempt → Problem target validation is unavailable."
                ),
                details={"problem_errors": problem_result.summary.errors},
            )
        )
        return problem_result, False, {}, issues

    registry = {doc.object_id: doc for doc in problem_result.documents if doc.object_id}
    return problem_result, True, registry, issues


def _legacy_file_issues(legacy_paths: list[Path], project_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in legacy_paths:
        rel = relative_to_root(path, project_root)
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="A-STOR-E001",
                message=(
                    f"Legacy per-Attempt file is not allowed in production storage: {path.name}. "
                    "Use Problem-scoped ledger Pxxxx.md."
                ),
                file=rel,
            )
        )
    return issues


def _build_documents_from_ledgers(
    project_root: Path,
    ledger_paths: list[Path],
) -> tuple[list[AttemptDocument], list[ValidationIssue]]:
    documents: list[AttemptDocument] = []
    issues: list[ValidationIssue] = []

    for path in ledger_paths:
        loaded = _load_ledger_file(path, project_root)
        issues.extend(loaded.issues)
        if loaded.issues:
            continue

        container_issues = validate_ledger_container(loaded)
        issues.extend(container_issues)
        documents.extend(expand_ledger_to_documents(loaded))

    return documents, issues


def _build_registry(documents: list[AttemptDocument]) -> dict[str, AttemptDocument]:
    registry: dict[str, AttemptDocument] = {}
    for doc in documents:
        if doc.object_id and doc.object_id not in registry:
            registry[doc.object_id] = doc
    return registry


def validate_project(
    root: Path | None = None,
    *,
    start_path: Path | None = None,
    focus_file: Path | None = None,
    problem_result: ProblemValidationResult | None = None,
) -> ValidationResult:
    project_root = resolve_project_root(root, start_path)
    ledger_paths = discover_markdown_files(project_root)
    legacy_paths = discover_legacy_attempt_files(project_root)

    pv_result, problem_healthy, problem_registry, dependency_issues = _resolve_problem(
        project_root, problem_result
    )

    documents, early_issues = _build_documents_from_ledgers(project_root, ledger_paths)

    result = ValidationResult(
        project_root=project_root,
        summary=ValidationSummary(markdown_files=len(ledger_paths)),
        documents=documents,
        problem_result=pv_result,
        dependency=DependencySummary(
            healthy=problem_healthy,
            errors=pv_result.summary.errors,
            warnings=pv_result.summary.warnings,
            problem_objects=pv_result.summary.problem_objects,
            result=pv_result.summary.result,
        ),
    )

    for issue in dependency_issues + _legacy_file_issues(legacy_paths, project_root) + early_issues:
        result.add_issue(issue)

    for doc in documents:
        for issue in validate_base(doc):
            result.add_issue(issue)
        for issue in validate_part_shape(doc):
            result.add_issue(issue)

    for issue in validate_unique_ids(documents):
        result.add_issue(issue)

    for doc in documents:
        for issue in validate_problem_relation(
            doc,
            problem_registry=problem_registry,
            problem_healthy=problem_healthy,
        ):
            result.add_issue(issue)

    result.summary.attempt_objects = len(documents)

    if focus_file is not None:
        apply_focus_filter(
            result,
            focus_file,
            included=ledger_paths,
        )

    result.finalize()
    if result.summary.errors == 0:
        result.registry = _build_registry(documents)
    return result


def apply_focus_filter(
    result: ValidationResult,
    focus_file: Path,
    *,
    included: list[Path] | None = None,
) -> None:
    focus = focus_file.expanduser().resolve()
    rel = relative_to_root(focus, result.project_root)
    result.focus_relative_path = rel

    if not any(d.path.resolve() == focus for d in result.documents) and focus.exists():
        included_resolved = [p.resolve() for p in (included or [])]
        if included is not None and focus not in included_resolved:
            result.add_issue(
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="A-DISC-E002",
                    message=f"check-file target is outside Attempt evidence root: {rel}",
                    file=rel,
                )
            )

    filtered: list[ValidationIssue] = []
    for issue in result.issues:
        if issue.file == rel:
            filtered.append(issue)
            continue
        if issue.rule_id == "A-ID-E001" and issue.details:
            files = issue.details.get("files") or []
            if rel in files:
                filtered.append(issue)
                continue
        if issue.rule_id == "A-PROB-E010":
            filtered.append(issue)
        if issue.rule_id == "A-STOR-E001" and issue.file == rel:
            filtered.append(issue)
    result.issues = filtered
    result.finalize()


def focus_view(result: ValidationResult, focus_file: Path) -> ValidationResult:
    view = ValidationResult(
        project_root=result.project_root,
        summary=ValidationSummary(
            markdown_files=result.summary.markdown_files,
            attempt_objects=result.summary.attempt_objects,
            errors=result.summary.errors,
            warnings=result.summary.warnings,
            info=result.summary.info,
            result=result.summary.result,
        ),
        documents=result.documents,
        registry=result.registry,
        dependency=result.dependency,
        problem_result=result.problem_result,
        issues=list(result.issues),
    )
    apply_focus_filter(view, focus_file)
    return view


def validate_file(
    path: Path,
    *,
    root: Path | None = None,
    problem_result: ProblemValidationResult | None = None,
) -> ValidationResult:
    target = path.expanduser().resolve()
    if not target.is_file():
        project_root = resolve_project_root(root, target if target.exists() else None)
        result = ValidationResult(
            project_root=project_root,
            summary=ValidationSummary(result="FAIL", errors=1),
            focus_relative_path=str(target),
        )
        result.add_issue(
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="A-DISC-E002",
                message=f"File not found: {target}",
                file=str(target),
            )
        )
        result.finalize()
        return result

    start = target.parent
    return validate_project(
        root=root,
        start_path=start,
        focus_file=target,
        problem_result=problem_result,
    )


def discovery_error_result(exc: DiscoveryError, root_hint: Path | None = None) -> ValidationResult:
    root = root_hint or Path.cwd()
    result = ValidationResult(
        project_root=root,
        summary=ValidationSummary(result="FAIL", errors=1),
    )
    result.add_issue(
        ValidationIssue(
            severity=Severity.ERROR,
            rule_id=exc.rule_id,
            message=exc.message,
        )
    )
    result.finalize()
    return result
