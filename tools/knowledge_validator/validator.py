"""Orchestration: discover → parse → object/relation/graph rules → result."""

from __future__ import annotations

from pathlib import Path

from .discovery import (
    DiscoveryError,
    discover_markdown_files,
    relative_to_root,
    resolve_project_root,
    skipped_without_metadata_issue,
)
from .models import KnowledgeDocument, Severity, ValidationIssue, ValidationResult, ValidationSummary
from .parser import is_knowledge_candidate, parse_markdown_file
from .rules_graph import find_prerequisite_cycles
from .rules_object import validate_object
from .rules_relation import validate_relations, validate_unique_ids


def _build_documents(
    project_root: Path,
    paths: list[Path],
    *,
    verbose: bool,
) -> tuple[list[KnowledgeDocument], list, int]:
    """Return documents, issues, skipped_count."""
    documents: list[KnowledgeDocument] = []
    issues = []
    skipped = 0

    for path in paths:
        parsed = parse_markdown_file(path, project_root)
        if parsed.issues:
            # Parse errors: if front matter was attempted, keep as issues.
            # If no data, may still not be a candidate.
            issues.extend(parsed.issues)
            if parsed.data is None:
                # Opening --- with errors still counts as scanned markdown with issues.
                continue

        if not parsed.has_front_matter or parsed.data is None:
            skipped += 1
            if verbose:
                issues.append(skipped_without_metadata_issue(parsed.relative_path))
            continue

        if not is_knowledge_candidate(parsed.data):
            skipped += 1
            if verbose:
                issues.append(skipped_without_metadata_issue(parsed.relative_path))
            continue

        doc = KnowledgeDocument(
            path=path,
            relative_path=parsed.relative_path,
            data=parsed.data,
        )
        documents.append(doc)

    return documents, issues, skipped


def validate_project(
    *,
    root: Path | None = None,
    start_path: Path | None = None,
    focus_file: Path | None = None,
    verbose: bool = False,
) -> ValidationResult:
    project_root = resolve_project_root(root, start_path)
    included, excluded = discover_markdown_files(project_root)

    documents, early_issues, skipped = _build_documents(
        project_root, included, verbose=verbose
    )

    result = ValidationResult(
        project_root=project_root,
        summary=ValidationSummary(
            markdown_files=len(included) + len(excluded),
            knowledge_objects=0,
            excluded_files=len(excluded),
            skipped_files=skipped,
        ),
        documents=documents,
    )
    for issue in early_issues:
        result.add_issue(issue)

    # Single-object rules first (populate object_id / lists)
    for doc in documents:
        for issue in validate_object(doc):
            result.add_issue(issue)

    # Registry: only docs with valid-looking IDs; still include duplicates for uniqueness check
    registry: dict[str, KnowledgeDocument] = {}
    for doc in documents:
        if doc.object_id is None:
            continue
        # Keep first for relation lookups; uniqueness reported separately
        registry.setdefault(doc.object_id, doc)

    for issue in validate_unique_ids(documents):
        result.add_issue(issue)

    for doc in documents:
        for issue in validate_relations(doc, registry):
            result.add_issue(issue)

    for issue in find_prerequisite_cycles(registry):
        result.add_issue(issue)

    result.summary.knowledge_objects = len(documents)

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
    """Narrow a full-project ValidationResult to check-file semantics (mutates result)."""
    focus = focus_file.expanduser().resolve()
    rel = relative_to_root(focus, result.project_root)
    result.focus_relative_path = rel
    documents = result.documents

    if not any(d.path.resolve() == focus for d in documents) and focus.exists():
        excluded_resolved = [p.resolve() for p in (excluded or [])]
        included_resolved = [p.resolve() for p in (included or [])]
        if focus in excluded_resolved:
            result.add_issue(
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="K-DISC-001",
                    message="check-file target is the Knowledge template, not a real Knowledge object.",
                    file=rel,
                )
            )
        elif included is not None and focus not in included_resolved:
            result.add_issue(
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="K-DISC-001",
                    message=f"check-file target is outside Knowledge library: {rel}",
                    file=rel,
                )
            )

    focus_ids = {d.object_id for d in documents if d.path.resolve() == focus and d.object_id}
    filtered = []
    for issue in result.issues:
        if issue.file == rel:
            filtered.append(issue)
            continue
        if issue.rule_id == "K-GRAPH-001" and issue.details:
            cycle = issue.details.get("cycle") or []
            if focus_ids.intersection(cycle):
                filtered.append(issue)
                continue
        if issue.rule_id == "K-BASE-040" and issue.object_id in focus_ids:
            filtered.append(issue)
            continue
    result.issues = filtered
    result.finalize()


def focus_view(result: ValidationResult, focus_file: Path) -> ValidationResult:
    """Return a check-file view of an already-computed full ValidationResult."""
    view = ValidationResult(
        project_root=result.project_root,
        summary=ValidationSummary(
            markdown_files=result.summary.markdown_files,
            knowledge_objects=result.summary.knowledge_objects,
            excluded_files=result.summary.excluded_files,
            skipped_files=result.summary.skipped_files,
        ),
        documents=result.documents,
        issues=list(result.issues),
    )
    apply_focus_filter(view, focus_file)
    return view


def validate_file(
    path: Path,
    *,
    root: Path | None = None,
    verbose: bool = False,
) -> ValidationResult:
    target = path.expanduser().resolve()
    if not target.is_file():
        project_root = resolve_project_root(root, target if target.exists() else None)
        from .models import Severity, ValidationIssue

        result = ValidationResult(
            project_root=project_root,
            summary=ValidationSummary(result="FAIL", errors=1),
            focus_relative_path=str(target),
        )
        result.add_issue(
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="K-DISC-001",
                message=f"File not found: {target}",
                file=str(target),
            )
        )
        result.finalize()
        return result

    start = target.parent
    return validate_project(root=root, start_path=start, focus_file=target, verbose=verbose)


def discovery_error_result(exc: DiscoveryError, root_hint: Path | None = None) -> ValidationResult:
    from .models import Severity, ValidationIssue

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
