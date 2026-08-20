"""Orchestration: validate → build model → render → publish / check."""

from __future__ import annotations

from pathlib import Path

from tools.knowledge_validator import (
    DiscoveryError,
    KnowledgeDocument,
    ValidationResult,
    resolve_project_root,
    validate_project,
)
from tools.knowledge_validator.constants import VALIDATOR_VERSION

from .builder import build_index_model
from .constants import INDEX_DIR_RELATIVE, INDEXER_VERSION, MANAGED_FILES
from .models import (
    IndexOperationResult,
    IndexResultKind,
    IndexerIssue,
    KnowledgeIndexModel,
    RenderedIndex,
)
from .publisher import PublishError, index_dir_path, publish_index, read_current_index_files
from .renderer_json import render_json
from .renderer_markdown import render_all_markdown
from .stale import compare_to_expected


def _registry_from_validation(result: ValidationResult) -> dict[str, KnowledgeDocument]:
    registry: dict[str, KnowledgeDocument] = {}
    for doc in result.documents:
        if doc.object_id is None:
            continue
        registry.setdefault(doc.object_id, doc)
    return {k: registry[k] for k in sorted(registry.keys())}


def render_snapshot(model: KnowledgeIndexModel) -> RenderedIndex:
    files = render_all_markdown(model)
    files["knowledge_index.json"] = render_json(model)
    # Ensure all managed files present
    for name in MANAGED_FILES:
        if name not in files:
            raise RuntimeError(f"Missing rendered file: {name}")
    return RenderedIndex(files=files)


def _fill_summary(op: IndexOperationResult, model: KnowledgeIndexModel | None) -> None:
    if model is None:
        return
    op.model = model
    op.knowledge_objects = model.knowledge_objects
    op.domains = len(model.domains)
    op.prerequisite_edges = model.prerequisite_edges
    op.related_declared_edges = model.related_declared_edges
    op.related_effective_edges = model.related_effective_edges


def _validate(
    *,
    root: Path | None,
    strict_warnings: bool,
) -> tuple[ValidationResult | None, IndexOperationResult | None]:
    try:
        project_root = resolve_project_root(root)
    except DiscoveryError as exc:
        op = IndexOperationResult(
            result=IndexResultKind.FAIL,
            project_root=str(root or Path.cwd()),
            index_dir=INDEX_DIR_RELATIVE,
            validator_result="FAIL",
            validator_errors=1,
        )
        op.issues.append(
            IndexerIssue(severity="ERROR", rule_id="KI-ROOT-001", message=exc.message)
        )
        return None, op

    result = validate_project(root=project_root)
    op_base = IndexOperationResult(
        result=IndexResultKind.FAIL,
        project_root=str(project_root),
        index_dir=INDEX_DIR_RELATIVE,
        validator_errors=result.summary.errors,
        validator_warnings=result.summary.warnings,
        validator_result=result.summary.result,
        validator_issues=list(result.issues),
    )

    if result.summary.errors > 0:
        op_base.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-VALIDATE-001",
                message="Knowledge Validator reported ERROR; index build/check aborted.",
            )
        )
        return None, op_base

    if strict_warnings and result.summary.warnings > 0:
        op_base.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-VALIDATE-002",
                message="--strict-warnings: Validator WARNING blocked indexing.",
            )
        )
        return None, op_base

    return result, None


def _index_from_validation(
    validation: ValidationResult,
    *,
    strict_warnings: bool,
    mode: str,
) -> IndexOperationResult:
    """Build or check index from an already-computed ValidationResult (no re-scan)."""
    project_root = validation.project_root
    op = IndexOperationResult(
        result=IndexResultKind.FAIL,
        project_root=str(project_root),
        index_dir=INDEX_DIR_RELATIVE,
        validator_errors=validation.summary.errors,
        validator_warnings=validation.summary.warnings,
        validator_result=validation.summary.result,
        validator_issues=list(validation.issues),
    )

    if validation.summary.errors > 0:
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-VALIDATE-001",
                message="Knowledge Validator reported ERROR; index build/check aborted.",
            )
        )
        return op

    if strict_warnings and validation.summary.warnings > 0:
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-VALIDATE-002",
                message="--strict-warnings: Validator WARNING blocked indexing.",
            )
        )
        return op

    try:
        registry = _registry_from_validation(validation)
        model = build_index_model(registry)
        rendered = render_snapshot(model)
    except Exception as exc:
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-BUILD-001",
                message=f"Index build failed: {exc}",
            )
        )
        return op

    _fill_summary(op, model)

    if mode == "check":
        kind, issues = compare_to_expected(project_root, rendered)
        op.result = kind
        op.issues.extend(issues)
        return op

    current = read_current_index_files(project_root)
    unexpected = []
    from .publisher import list_unexpected_files

    if index_dir_path(project_root).is_dir():
        unexpected = list_unexpected_files(project_root)

    if (
        current is not None
        and not unexpected
        and set(current.keys()) == set(rendered.files.keys())
        and all(current[k] == rendered.files[k] for k in rendered.files)
    ):
        op.result = IndexResultKind.UP_TO_DATE
        return op

    try:
        publish_index(project_root, rendered)
    except PublishError as exc:
        op.issues.append(
            IndexerIssue(severity="ERROR", rule_id=exc.rule_id, message=exc.message)
        )
        return op
    except Exception as exc:
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-PUBLISH-001",
                message=f"Publish failed: {exc}",
            )
        )
        return op

    op.result = IndexResultKind.BUILT
    return op


def build_from_validation(
    validation: ValidationResult,
    *,
    strict_warnings: bool = False,
) -> IndexOperationResult:
    return _index_from_validation(validation, strict_warnings=strict_warnings, mode="build")


def check_from_validation(
    validation: ValidationResult,
    *,
    strict_warnings: bool = False,
) -> IndexOperationResult:
    return _index_from_validation(validation, strict_warnings=strict_warnings, mode="check")


def build_expected(
    *,
    root: Path | None = None,
    strict_warnings: bool = False,
) -> tuple[IndexOperationResult, RenderedIndex | None, Path | None]:
    validation, fail = _validate(root=root, strict_warnings=strict_warnings)
    if fail is not None:
        return fail, None, None

    assert validation is not None
    project_root = validation.project_root
    try:
        registry = _registry_from_validation(validation)
        model = build_index_model(registry)
        rendered = render_snapshot(model)
    except Exception as exc:
        op = IndexOperationResult(
            result=IndexResultKind.FAIL,
            project_root=str(project_root),
            index_dir=INDEX_DIR_RELATIVE,
            validator_errors=validation.summary.errors,
            validator_warnings=validation.summary.warnings,
            validator_result=validation.summary.result,
            validator_issues=list(validation.issues),
        )
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="KI-BUILD-001",
                message=f"Index build failed: {exc}",
            )
        )
        return op, None, None

    op = IndexOperationResult(
        result=IndexResultKind.BUILT,
        project_root=str(project_root),
        index_dir=INDEX_DIR_RELATIVE,
        validator_errors=validation.summary.errors,
        validator_warnings=validation.summary.warnings,
        validator_result=validation.summary.result,
        validator_issues=list(validation.issues),
    )
    _fill_summary(op, model)
    return op, rendered, project_root


def build_index(
    *,
    root: Path | None = None,
    strict_warnings: bool = False,
) -> IndexOperationResult:
    validation, fail = _validate(root=root, strict_warnings=strict_warnings)
    if fail is not None:
        return fail
    assert validation is not None
    return build_from_validation(validation, strict_warnings=strict_warnings)


def check_index(
    *,
    root: Path | None = None,
    strict_warnings: bool = False,
) -> IndexOperationResult:
    validation, fail = _validate(root=root, strict_warnings=strict_warnings)
    if fail is not None:
        return fail
    assert validation is not None
    return check_from_validation(validation, strict_warnings=strict_warnings)
