"""Thin deterministic orchestration: mutation → auto changed-set → finalizer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.attempt_validator import append_attempt_to_ledger
from tools.latex_build import build_latex_project
from tools.latex_build.models import PublishStatus
from tools.problem_solution import upsert_canonical_solution
from tools.problem_solution.models import UpsertAction

from .finalizer import finalize
from .operation_models import (
    ArtifactStatus,
    AttemptRecordStatus,
    OperationResult,
    PersistenceStatus,
)


def _attach_reconcile(result: OperationResult, recon) -> OperationResult:
    result.reconcile = recon
    result.canonical_coverage = (
        "COMPLETE" if recon.completion.complete else "INCOMPLETE"
    )
    result.workflow = recon.workflow_after or recon.workflow_before
    if recon.artifact:
        result.latex = recon.artifact.latex.value
        result.pdf = recon.artifact.pdf.value
        if recon.artifact.paths and recon.artifact.pdf.value == "CURRENT":
            result.artifact = ArtifactStatus.COMPLETE
            result.artifact_path = str(recon.artifact.paths.formal_pdf)
        elif recon.artifact.pdf.value == "FAILED":
            result.artifact = ArtifactStatus.FAILED
        elif recon.artifact.pdf.value in {"NOT_APPLICABLE", "SKIPPED"}:
            result.artifact = ArtifactStatus.NOT_REQUESTED
    if recon.finalize is not None:
        result.finalize = recon.finalize
    return result


def persist_canonical_solution_op(
    root: Path | str,
    *,
    problem_id: str,
    content: str,
    part: str | None = None,
    include_verification: bool = False,
    auto_reconcile: bool = True,
    auto_close: bool = True,
    auto_artifact: bool = True,
    math_self_check_ok: bool = True,
    artifact_domain: str | None = None,
) -> OperationResult:
    """Upsert canonical Solution; source-finalize if written; always reconcile by default."""
    from tools.normal_operation.reconcile import reconcile_problem

    project_root = Path(root).resolve()
    upsert = upsert_canonical_solution(
        project_root,
        problem_id=problem_id,
        content=content,
        part=part,
    )
    target = upsert.target
    result = OperationResult(
        persistence_target=target,
        persistence_path=upsert.problem_path or None,
    )
    if upsert.error:
        result.persistence = PersistenceStatus.FAILED
        result.error = upsert.error
        return result

    if upsert.written:
        if upsert.action == UpsertAction.UPDATE:
            result.persistence = PersistenceStatus.CORRECTED
        else:
            result.persistence = PersistenceStatus.WRITTEN
        result.changed_types = ["problem"]
        result.finalize = finalize(
            root=project_root,
            changed=["problem"],
            include_verification=False,
        )
    else:
        result.persistence = PersistenceStatus.NO_OP
        result.changed_types = []

    if auto_reconcile:
        recon = reconcile_problem(
            project_root,
            problem_id=problem_id,
            math_self_check_ok=math_self_check_ok,
            auto_close=auto_close,
            auto_artifact=auto_artifact,
            artifact_domain=artifact_domain,
            include_verification=include_verification,
        )
        return _attach_reconcile(result, recon)
    return result


def record_user_attempt_op(
    root: Path | str,
    *,
    problem_id: str,
    record: dict[str, Any],
    narrative: str,
    include_verification: bool = False,
) -> OperationResult:
    """Append one user Attempt; auto-finalize on success."""
    project_root = Path(root).resolve()
    append = append_attempt_to_ledger(
        project_root,
        problem_id=problem_id,
        record=record,
        narrative=narrative,
    )
    result = OperationResult(
        attempt_id=append.attempt_id,
        attempt_ledger_path=append.ledger_path,
    )
    if not append.written:
        result.attempt = AttemptRecordStatus.FAILED
        result.error = append.error
        return result

    result.attempt = AttemptRecordStatus.CREATED
    result.changed_types = ["attempt"]
    result.finalize = finalize(
        root=project_root,
        changed=["attempt"],
        include_verification=include_verification,
    )
    return result


def study_to_auto_op(
    root: Path | str,
    *,
    problem_id: str,
    part: str | None,
    record: dict[str, Any],
    narrative: str,
    solution_content: str,
    include_verification: bool = False,
) -> OperationResult:
    """Freeze one STUDY Attempt then persist canonical Solution; single finalizer chain."""
    project_root = Path(root).resolve()
    result = OperationResult()

    append = append_attempt_to_ledger(
        project_root,
        problem_id=problem_id,
        record=record,
        narrative=narrative,
    )
    if not append.written:
        result.attempt = AttemptRecordStatus.FAILED
        result.error = append.error
        return result
    result.attempt = AttemptRecordStatus.CREATED
    result.attempt_id = append.attempt_id
    result.attempt_ledger_path = append.ledger_path
    changed: list[str] = ["attempt"]

    upsert = upsert_canonical_solution(
        project_root,
        problem_id=problem_id,
        content=solution_content,
        part=part,
    )
    result.persistence_target = upsert.target
    result.persistence_path = upsert.problem_path or None
    if upsert.error:
        result.persistence = PersistenceStatus.FAILED
        result.error = upsert.error
        return result
    if upsert.written:
        result.persistence = PersistenceStatus.WRITTEN
        changed.append("problem")
    else:
        result.persistence = PersistenceStatus.NO_OP

    result.changed_types = changed
    result.finalize = finalize(
        root=project_root,
        changed=changed,
        include_verification=include_verification,
    )
    return result


def publish_pdf_op(
    root: Path | str,
    *,
    latex_project: Path | str,
    changed_before_build: list[str] | None = None,
    include_verification: bool = False,
) -> OperationResult:
    """After explicit PDF authorization: finalize changed types → P9 build."""
    project_root = Path(root).resolve()
    result = OperationResult(artifact=ArtifactStatus.NOT_REQUESTED)
    changed = list(changed_before_build or [])
    if changed:
        result.changed_types = changed
        result.finalize = finalize(
            root=project_root,
            changed=changed,
            include_verification=include_verification,
        )
        if result.finalize.validation_status.value == "FAIL" or result.finalize.workspace_check_status.value == "FAIL":
            result.artifact = ArtifactStatus.FAILED
            result.error = "finalization failed before PDF build"
            return result

    build = build_latex_project(Path(latex_project), repo_root=project_root)
    published = (
        build.compile_result.success
        and build.publish_result is not None
        and build.publish_result.status
        in {PublishStatus.CREATED, PublishStatus.UPDATED, PublishStatus.UP_TO_DATE}
    )
    if published:
        result.artifact = ArtifactStatus.COMPLETE
        result.artifact_path = str(build.publish_result.formal_pdf)
    else:
        result.artifact = ArtifactStatus.FAILED
        result.error = "LaTeX build failed"
    return result
