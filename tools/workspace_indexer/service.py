"""Orchestration for Workspace Indexer v1.5.

Orchestration order (implementation, not Schema dependency):
  Knowledge → Problem → Attempt → Method → snapshot → render → publish

Semantic dependency:
  Knowledge → Problem → Attempt
  Knowledge → Method
  Method does not depend on Problem or Attempt.
  Descriptive Derived Evidence depends on Problem + Attempt only.
  Knowledge Associated Evidence depends on Knowledge + Problem + Attempt + DerivedEvidenceSnapshot.
  Formal Knowledge Relations depend on Knowledge + Problem + Method validated registries only.
"""

from __future__ import annotations

from pathlib import Path

from tools.attempt_validator import validate_project as validate_attempt_project
from tools.derived_evidence.builder import DerivedEvidenceBuildError
from tools.knowledge_relations.builder import KnowledgeRelationBuildError
from tools.knowledge_validator import resolve_project_root, validate_project as validate_knowledge_project
from tools.knowledge_validator.discovery import DiscoveryError
from tools.method_validator import validate_project as validate_method_project
from tools.problem_validator import validate_project as validate_problem_project

from .builder import build_workspace_snapshot
from .constants import INDEX_DIR_RELATIVE
from .models import IndexOperationResult, IndexResultKind, IndexerIssue, RenderedWorkspaceIndex
from .publisher import compare_to_disk, publish_index, read_current_files
from .renderer import render_all


def _fail_op(project_root: Path | str, message: str, rule_id: str) -> IndexOperationResult:
    return IndexOperationResult(
        result=IndexResultKind.FAIL,
        project_root=str(project_root),
        index_dir=INDEX_DIR_RELATIVE,
        issues=[IndexerIssue(severity="ERROR", rule_id=rule_id, message=message)],
    )


def _validate_all(
    project_root: Path,
) -> tuple[IndexOperationResult | None, object | None, object | None, object | None, object | None]:
    knowledge_result = validate_knowledge_project(root=project_root)
    if knowledge_result.summary.errors > 0:
        op = IndexOperationResult(
            result=IndexResultKind.FAIL,
            project_root=str(project_root),
            index_dir=INDEX_DIR_RELATIVE,
            knowledge_validator_result=knowledge_result.summary.result,
            knowledge_errors=knowledge_result.summary.errors,
        )
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="WI-VALIDATE-001",
                message="Knowledge Validator reported ERROR; workspace index aborted.",
            )
        )
        return op, None, None, None, None

    problem_result = validate_problem_project(root=project_root, knowledge_result=knowledge_result)
    if problem_result.summary.errors > 0:
        op = IndexOperationResult(
            result=IndexResultKind.FAIL,
            project_root=str(project_root),
            index_dir=INDEX_DIR_RELATIVE,
            knowledge_validator_result=knowledge_result.summary.result,
            problem_validator_result=problem_result.summary.result,
            knowledge_errors=knowledge_result.summary.errors,
            problem_errors=problem_result.summary.errors,
        )
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="WI-VALIDATE-002",
                message="Problem Validator reported ERROR; workspace index aborted.",
            )
        )
        return op, None, None, None, None

    attempt_result = validate_attempt_project(
        root=project_root,
        problem_result=problem_result,
    )
    if attempt_result.summary.errors > 0:
        op = IndexOperationResult(
            result=IndexResultKind.FAIL,
            project_root=str(project_root),
            index_dir=INDEX_DIR_RELATIVE,
            knowledge_validator_result=knowledge_result.summary.result,
            problem_validator_result=problem_result.summary.result,
            attempt_validator_result=attempt_result.summary.result,
            knowledge_errors=knowledge_result.summary.errors,
            problem_errors=problem_result.summary.errors,
            attempt_errors=attempt_result.summary.errors,
        )
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="WI-VALIDATE-003",
                message="Attempt Validator reported ERROR; workspace index aborted.",
            )
        )
        return op, None, None, None, None

    method_result = validate_method_project(
        root=project_root,
        knowledge_result=knowledge_result,
    )
    if method_result.summary.errors > 0:
        op = IndexOperationResult(
            result=IndexResultKind.FAIL,
            project_root=str(project_root),
            index_dir=INDEX_DIR_RELATIVE,
            knowledge_validator_result=knowledge_result.summary.result,
            problem_validator_result=problem_result.summary.result,
            attempt_validator_result=attempt_result.summary.result,
            method_validator_result=method_result.summary.result,
            knowledge_errors=knowledge_result.summary.errors,
            problem_errors=problem_result.summary.errors,
            attempt_errors=attempt_result.summary.errors,
            method_errors=method_result.summary.errors,
        )
        op.issues.append(
            IndexerIssue(
                severity="ERROR",
                rule_id="WI-VALIDATE-004",
                message="Method Validator reported ERROR; workspace index aborted.",
            )
        )
        return op, None, None, None, None

    return None, knowledge_result, problem_result, attempt_result, method_result


def _build_rendered(
    project_root: Path,
    knowledge_result,
    problem_result,
    attempt_result,
    method_result,
) -> RenderedWorkspaceIndex | IndexOperationResult:
    try:
        snapshot = build_workspace_snapshot(
            project_root,
            knowledge_result=knowledge_result,
            problem_result=problem_result,
            attempt_result=attempt_result,
            method_result=method_result,
        )
    except (DerivedEvidenceBuildError, KnowledgeRelationBuildError) as exc:
        meta = _success_meta(knowledge_result, problem_result, attempt_result, method_result)
        kind = "derived evidence" if isinstance(exc, DerivedEvidenceBuildError) else "knowledge relations"
        rule_id = "WI-DERIVE-001" if isinstance(exc, DerivedEvidenceBuildError) else "WI-DERIVE-002"
        op = IndexOperationResult(
            result=IndexResultKind.FAIL,
            project_root=str(project_root),
            index_dir=INDEX_DIR_RELATIVE,
            issues=[
                IndexerIssue(
                    severity="ERROR",
                    rule_id=rule_id,
                    message=f"{kind} build failed: {exc}",
                )
            ],
            **meta,
        )
        return op
    return RenderedWorkspaceIndex(files=render_all(snapshot))


def _success_meta(
    knowledge_result,
    problem_result,
    attempt_result,
    method_result,
) -> dict[str, object]:
    return {
        "knowledge_validator_result": knowledge_result.summary.result,
        "problem_validator_result": problem_result.summary.result,
        "attempt_validator_result": attempt_result.summary.result,
        "method_validator_result": method_result.summary.result,
    }


def build_expected_outputs(root: Path | None = None) -> tuple[IndexOperationResult, dict[str, str] | None]:
    try:
        project_root = resolve_project_root(root)
    except DiscoveryError as exc:
        op = _fail_op(root or Path.cwd(), exc.message, "WI-ROOT-001")
        return op, None

    fail, knowledge_result, problem_result, attempt_result, method_result = _validate_all(project_root)
    if fail is not None:
        return fail, None

    assert (
        knowledge_result is not None
        and problem_result is not None
        and attempt_result is not None
        and method_result is not None
    )
    rendered = _build_rendered(
        project_root, knowledge_result, problem_result, attempt_result, method_result
    )
    if isinstance(rendered, IndexOperationResult):
        return rendered, None
    meta = _success_meta(knowledge_result, problem_result, attempt_result, method_result)
    return IndexOperationResult(
        result=IndexResultKind.BUILT,
        project_root=str(project_root),
        index_dir=INDEX_DIR_RELATIVE,
        **meta,
    ), rendered.files


def build_workspace_snapshot_from_root(root: Path | None = None):
    """Public API: validated snapshot for reuse by workspace_check."""
    project_root = resolve_project_root(root)
    fail, knowledge_result, problem_result, attempt_result, method_result = _validate_all(project_root)
    if fail is not None:
        raise RuntimeError("Validation failed; cannot build workspace snapshot")

    assert (
        knowledge_result is not None
        and problem_result is not None
        and attempt_result is not None
        and method_result is not None
    )
    return build_workspace_snapshot(
        project_root,
        knowledge_result=knowledge_result,
        problem_result=problem_result,
        attempt_result=attempt_result,
        method_result=method_result,
    )


def check_index(*, root: Path | None = None) -> IndexOperationResult:
    try:
        project_root = resolve_project_root(root)
    except DiscoveryError as exc:
        return _fail_op(root or Path.cwd(), exc.message, "WI-ROOT-001")

    fail, knowledge_result, problem_result, attempt_result, method_result = _validate_all(project_root)
    if fail is not None:
        return fail

    assert (
        knowledge_result is not None
        and problem_result is not None
        and attempt_result is not None
        and method_result is not None
    )
    rendered = _build_rendered(
        project_root, knowledge_result, problem_result, attempt_result, method_result
    )
    if isinstance(rendered, IndexOperationResult):
        return rendered
    kind_str, issues = compare_to_disk(project_root, rendered)
    kind = IndexResultKind(kind_str)
    meta = _success_meta(knowledge_result, problem_result, attempt_result, method_result)
    return IndexOperationResult(
        result=kind,
        project_root=str(project_root),
        index_dir=INDEX_DIR_RELATIVE,
        issues=issues,
        **meta,
    )


def _publish_if_needed(
    project_root: Path,
    rendered: RenderedWorkspaceIndex,
    *,
    knowledge_result,
    problem_result,
    attempt_result,
    method_result,
) -> IndexOperationResult:
    current = read_current_files(project_root)
    meta = _success_meta(knowledge_result, problem_result, attempt_result, method_result)
    if current is not None:
        if set(current.keys()) == set(rendered.files.keys()) and all(
            current[k] == rendered.files[k] for k in rendered.files
        ):
            return IndexOperationResult(
                result=IndexResultKind.UP_TO_DATE,
                project_root=str(project_root),
                index_dir=INDEX_DIR_RELATIVE,
                **meta,
            )

    publish_index(project_root, rendered)
    return IndexOperationResult(
        result=IndexResultKind.BUILT,
        project_root=str(project_root),
        index_dir=INDEX_DIR_RELATIVE,
        **meta,
    )


def rebuild_index(*, root: Path | None = None) -> IndexOperationResult:
    try:
        project_root = resolve_project_root(root)
    except DiscoveryError as exc:
        return _fail_op(root or Path.cwd(), exc.message, "WI-ROOT-001")

    fail, knowledge_result, problem_result, attempt_result, method_result = _validate_all(project_root)
    if fail is not None:
        return fail

    assert (
        knowledge_result is not None
        and problem_result is not None
        and attempt_result is not None
        and method_result is not None
    )
    rendered = _build_rendered(
        project_root, knowledge_result, problem_result, attempt_result, method_result
    )
    if isinstance(rendered, IndexOperationResult):
        return rendered
    return _publish_if_needed(
        project_root,
        rendered,
        knowledge_result=knowledge_result,
        problem_result=problem_result,
        attempt_result=attempt_result,
        method_result=method_result,
    )


def sync_index(*, root: Path | None = None) -> IndexOperationResult:
    """Validate sources; publish generated views only when stale or missing."""
    return rebuild_index(root=root)
