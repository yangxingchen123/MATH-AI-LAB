"""Candidate readiness and full-project orchestration for Gate v0.1."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.knowledge_validator.validator import validate_project as validate_knowledge_project

from .checks import (
    validate_base,
    validate_content_review_marker,
    validate_directory_info,
    validate_knowledge,
    validate_legacy_filename,
    validate_parts,
    validate_unique_ids,
)
from .constants import MANUAL_REVIEW_ITEMS
from .discovery import (
    DiscoveryError,
    discover_markdown_files,
    is_template_file,
    relative_to_root,
    resolve_project_root,
)
from .models import GateIssue, GateResult, GateSummary, ProblemDocument, Severity
from .parser import is_problem_candidate, parse_markdown_file


def load_knowledge_registry(project_root: Path) -> tuple[bool, dict[str, Any], list[GateIssue]]:
    """Reuse Knowledge Validator v1.1 public API. Do not reimplement Knowledge Schema."""
    kv = validate_knowledge_project(root=project_root)
    issues: list[GateIssue] = []
    healthy = kv.summary.errors == 0
    if not healthy:
        issues.append(
            GateIssue(
                severity=Severity.ERROR,
                rule_id="PCG-KNOW-E010",
                message=(
                    "Knowledge Validator reported ERROR; Problem Candidate Gate will not "
                    "treat Knowledge registry relations as reliable (DEPENDENCY FAILED)."
                ),
                details={"knowledge_errors": kv.summary.errors},
            )
        )
        return False, {}, issues
    registry = {doc.object_id: doc for doc in kv.documents if doc.object_id}
    return True, registry, issues


def _build_documents(
    project_root: Path,
    paths: list[Path],
    *,
    verbose: bool,
) -> tuple[list[ProblemDocument], list[GateIssue], int]:
    documents: list[ProblemDocument] = []
    issues: list[GateIssue] = []
    skipped = 0

    for path in paths:
        parsed = parse_markdown_file(path, project_root)
        if parsed.issues:
            issues.extend(parsed.issues)
            if parsed.data is None:
                continue

        if not parsed.has_front_matter or parsed.data is None:
            skipped += 1
            issues.append(
                GateIssue(
                    severity=Severity.WARNING,
                    rule_id="PCG-DISC-W001",
                    message="Markdown without Problem Candidate metadata.",
                    file=parsed.relative_path,
                )
            )
            continue

        if not is_problem_candidate(parsed.data):
            skipped += 1
            if verbose:
                issues.append(
                    GateIssue(
                        severity=Severity.INFO,
                        rule_id="PCG-DISC-W001",
                        message="Skipped Markdown whose YAML is not a Problem Candidate.",
                        file=parsed.relative_path,
                    )
                )
            continue

        documents.append(
            ProblemDocument(
                path=path,
                relative_path=parsed.relative_path,
                data=parsed.data,
                body=parsed.body,
            )
        )

    return documents, issues, skipped


def run_gate(
    *,
    root: Path | None = None,
    start_path: Path | None = None,
    focus_file: Path | None = None,
    verbose: bool = False,
    include_manual_review: bool = False,
) -> GateResult:
    project_root = resolve_project_root(root, start_path)
    included, excluded = discover_markdown_files(project_root)
    documents, early_issues, skipped = _build_documents(
        project_root, included, verbose=verbose
    )

    result = GateResult(
        project_root=project_root,
        summary=GateSummary(
            markdown_files=len(included) + len(excluded),
            problem_candidates=0,
            excluded_files=len(excluded),
            skipped_files=skipped,
        ),
        documents=documents,
        manual_review_items=list(MANUAL_REVIEW_ITEMS) if include_manual_review else [],
    )
    for issue in early_issues:
        result.add_issue(issue)

    knowledge_healthy, knowledge_registry, kv_issues = load_knowledge_registry(project_root)
    result.knowledge_dependency_ok = knowledge_healthy
    for issue in kv_issues:
        result.add_issue(issue)

    for doc in documents:
        for issue in validate_base(doc):
            result.add_issue(issue)
        for issue in validate_knowledge(
            doc,
            knowledge_registry=knowledge_registry,
            knowledge_healthy=knowledge_healthy,
        ):
            result.add_issue(issue)
        for issue in validate_parts(doc):
            result.add_issue(issue)
        for issue in validate_legacy_filename(doc):
            result.add_issue(issue)
        for issue in validate_content_review_marker(doc):
            result.add_issue(issue)
        for issue in validate_directory_info(doc, verbose=verbose):
            result.add_issue(issue)

    for issue in validate_unique_ids(documents):
        result.add_issue(issue)

    result.summary.problem_candidates = len(documents)

    if focus_file is not None:
        apply_focus_filter(result, focus_file, included=included, excluded=excluded)

    result.finalize()
    return result


def apply_focus_filter(
    result: GateResult,
    focus_file: Path,
    *,
    included: list[Path] | None = None,
    excluded: list[Path] | None = None,
) -> None:
    focus = focus_file.expanduser().resolve()
    rel = relative_to_root(focus, result.project_root)
    result.focus_relative_path = rel

    if is_template_file(focus, result.project_root):
        result.add_issue(
            GateIssue(
                severity=Severity.ERROR,
                rule_id="PCG-DISC-002",
                message="check-file target is the Problem template, not a real Problem candidate.",
                file=rel,
            )
        )
        return

    excluded_resolved = [p.resolve() for p in (excluded or [])]
    included_resolved = [p.resolve() for p in (included or [])]
    if focus not in included_resolved and focus not in excluded_resolved:
        if not focus.exists():
            result.add_issue(
                GateIssue(
                    severity=Severity.ERROR,
                    rule_id="PCG-DISC-002",
                    message=f"check-file target does not exist: {rel}",
                    file=rel,
                )
            )
            return
        result.add_issue(
            GateIssue(
                severity=Severity.ERROR,
                rule_id="PCG-DISC-002",
                message="check-file target is not a scanned Problem Markdown under 02_题目库/.",
                file=rel,
            )
        )
        return

    # Keep global uniqueness / knowledge-dependency issues; drop other files' local issues
    # except duplicate-ID details that mention this file.
    keep: list[GateIssue] = []
    for issue in result.issues:
        if issue.rule_id == "PCG-KNOW-E010":
            keep.append(issue)
            continue
        if issue.file == rel:
            keep.append(issue)
            continue
        if issue.rule_id == "PCG-ID-001" and issue.details.get("files"):
            if rel in issue.details["files"]:
                keep.append(issue)
    result.issues = keep
    result.documents = [d for d in result.documents if d.path.resolve() == focus]


def check_project(*, root: Path | None = None, verbose: bool = False) -> GateResult:
    return run_gate(root=root, verbose=verbose, include_manual_review=False)


def check_file(path: Path, *, root: Path | None = None, verbose: bool = False) -> GateResult:
    return run_gate(root=root, start_path=path, focus_file=path, verbose=verbose, include_manual_review=False)


def status_project(*, root: Path | None = None, verbose: bool = False) -> GateResult:
    return run_gate(root=root, verbose=verbose, include_manual_review=True)
