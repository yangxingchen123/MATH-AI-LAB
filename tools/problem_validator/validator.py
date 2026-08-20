"""Orchestration: Knowledge dependency → discover → parse → validate → result."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from tools.knowledge_validator.models import ValidationResult as KnowledgeValidationResult
from tools.knowledge_validator.validator import validate_project as validate_knowledge_project

from .discovery import (
    DiscoveryError,
    discover_markdown_files,
    is_template_file,
    relative_to_root,
    resolve_project_root,
)
from .models import (
    DependencySummary,
    ProblemDocument,
    Severity,
    ValidationIssue,
    ValidationResult,
    ValidationSummary,
)
from .parser import parse_markdown_file
from .rules_object import validate_base, validate_knowledge, validate_parts, validate_unique_ids

# Injectable for parse-once tests.
_parse_markdown_file: Callable[..., object] = parse_markdown_file


def set_parse_markdown_file_for_tests(fn: Callable[..., object] | None) -> None:
    global _parse_markdown_file
    _parse_markdown_file = fn or parse_markdown_file


def _resolve_knowledge(
    project_root: Path,
    knowledge_result: KnowledgeValidationResult | None,
) -> tuple[KnowledgeValidationResult, bool, dict[str, object], list[ValidationIssue]]:
    if knowledge_result is None:
        knowledge_result = validate_knowledge_project(root=project_root)

    issues: list[ValidationIssue] = []
    healthy = knowledge_result.summary.errors == 0
    if not healthy:
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="P-KNOW-E010",
                message=(
                    "Knowledge dependency validation failed; "
                    "Problem → Knowledge target validation is unavailable."
                ),
                details={"knowledge_errors": knowledge_result.summary.errors},
            )
        )
        return knowledge_result, False, {}, issues

    registry = {doc.object_id: doc for doc in knowledge_result.documents if doc.object_id}
    return knowledge_result, True, registry, issues


def _build_registry(documents: list[ProblemDocument]) -> dict[str, list[ProblemDocument]]:
    registry: dict[str, list[ProblemDocument]] = {}
    for doc in documents:
        if doc.object_id:
            registry.setdefault(doc.object_id, []).append(doc)
    return registry


def _build_documents(
    project_root: Path,
    paths: list[Path],
) -> tuple[list[ProblemDocument], list[ValidationIssue]]:
    documents: list[ProblemDocument] = []
    issues: list[ValidationIssue] = []

    for path in paths:
        parsed = _parse_markdown_file(path, project_root)
        if parsed.issues:
            issues.extend(parsed.issues)
            if parsed.data is None:
                continue

        if parsed.data is None:
            continue

        documents.append(
            ProblemDocument(
                path=path,
                relative_path=parsed.relative_path,
                data=parsed.data,
                body=parsed.body,
            )
        )

    return documents, issues


def validate_project(
    root: Path | None = None,
    *,
    start_path: Path | None = None,
    focus_file: Path | None = None,
    knowledge_result: KnowledgeValidationResult | None = None,
) -> ValidationResult:
    project_root = resolve_project_root(root, start_path)
    included, excluded = discover_markdown_files(project_root)

    kv_result, knowledge_healthy, knowledge_registry, dependency_issues = _resolve_knowledge(
        project_root, knowledge_result
    )

    documents, early_issues = _build_documents(project_root, included)

    result = ValidationResult(
        project_root=project_root,
        summary=ValidationSummary(
            markdown_files=len(included) + len(excluded),
            excluded_files=len(excluded),
        ),
        documents=documents,
        knowledge_result=kv_result,
        dependency=DependencySummary(
            healthy=knowledge_healthy,
            errors=kv_result.summary.errors,
            warnings=kv_result.summary.warnings,
            knowledge_objects=kv_result.summary.knowledge_objects,
            result=kv_result.summary.result,
        ),
    )

    for issue in dependency_issues + early_issues:
        result.add_issue(issue)

    for doc in documents:
        for issue in validate_base(doc):
            result.add_issue(issue)

    for issue in validate_unique_ids(documents):
        result.add_issue(issue)

    for doc in documents:
        for issue in validate_knowledge(
            doc,
            knowledge_registry=knowledge_registry,
            knowledge_healthy=knowledge_healthy,
        ):
            result.add_issue(issue)
        for issue in validate_parts(doc):
            result.add_issue(issue)

    result.registry = _build_registry(documents)
    result.summary.problem_objects = len(documents)

    if focus_file is not None:
        apply_focus_filter(
            result,
            focus_file,
            included=included,
            excluded=excluded,
        )

    result.finalize()
    return result


def apply_focus_filter(
    result: ValidationResult,
    focus_file: Path,
    *,
    included: list[Path] | None = None,
    excluded: list[Path] | None = None,
) -> None:
    focus = focus_file.expanduser().resolve()
    rel = relative_to_root(focus, result.project_root)
    result.focus_relative_path = rel

    if not any(d.path.resolve() == focus for d in result.documents) and focus.exists():
        excluded_resolved = [p.resolve() for p in (excluded or [])]
        included_resolved = [p.resolve() for p in (included or [])]
        if focus in excluded_resolved:
            result.add_issue(
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="P-DISC-E002",
                    message="check-file target is the Problem template, not a real Problem object.",
                    file=rel,
                )
            )
        elif included is not None and focus not in included_resolved:
            result.add_issue(
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="P-DISC-E002",
                    message=f"check-file target is outside Problem library: {rel}",
                    file=rel,
                )
            )

    filtered: list[ValidationIssue] = []
    for issue in result.issues:
        if issue.file == rel:
            filtered.append(issue)
            continue
        if issue.rule_id == "P-ID-E001" and issue.details:
            files = issue.details.get("files") or []
            if rel in files:
                filtered.append(issue)
                continue
        if issue.rule_id == "P-KNOW-E010":
            filtered.append(issue)
    result.issues = filtered
    result.finalize()


def focus_view(result: ValidationResult, focus_file: Path) -> ValidationResult:
    view = ValidationResult(
        project_root=result.project_root,
        summary=ValidationSummary(
            markdown_files=result.summary.markdown_files,
            problem_objects=result.summary.problem_objects,
            excluded_files=result.summary.excluded_files,
            errors=result.summary.errors,
            warnings=result.summary.warnings,
            info=result.summary.info,
            result=result.summary.result,
        ),
        documents=result.documents,
        registry=result.registry,
        dependency=result.dependency,
        knowledge_result=result.knowledge_result,
        issues=list(result.issues),
    )
    apply_focus_filter(view, focus_file)
    return view


def validate_file(
    path: Path,
    *,
    root: Path | None = None,
    knowledge_result: KnowledgeValidationResult | None = None,
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
                rule_id="P-DISC-E002",
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
        knowledge_result=knowledge_result,
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
