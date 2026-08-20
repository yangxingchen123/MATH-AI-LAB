"""Problem reconciliation: completion → workflow → artifact (check-first)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from tools.problem_solution.writer import find_problem_file
from tools.problem_validator import validate_file

from .artifact import (
    ArtifactReconcileResult,
    FreshnessState,
    inspect_artifact,
    reconcile_artifact,
)
from .completion import CompletionInspection, inspect_problem_completion
from .finalizer import finalize
from .models import FinalizeResult
from .workflow import WorkflowMoveResult, move_problem_to_workflow, workflow_from_relative


@dataclass
class ReconcileCounters:
    source_writes: int = 0
    workflow_moves: int = 0
    latex_writes: int = 0
    builds: int = 0
    pdf_replaces: int = 0
    workspace_syncs: int = 0


@dataclass
class ReconcileResult:
    problem_id: str
    completion: CompletionInspection
    workflow_before: str = ""
    workflow_after: str = ""
    workflow_move: WorkflowMoveResult | None = None
    artifact: ArtifactReconcileResult | None = None
    finalize: FinalizeResult | None = None
    counters: ReconcileCounters = field(default_factory=ReconcileCounters)
    skipped_archive: bool = False
    error: str | None = None

    @property
    def overall_pass(self) -> bool:
        if self.error:
            return False
        if self.artifact and self.artifact.pdf == FreshnessState.FAILED:
            return False
        if self.finalize and not self.finalize.overall_pass:
            return False
        return True


def reconcile_problem(
    root: Path | str,
    *,
    problem_id: str,
    math_self_check_ok: bool = True,
    auto_close: bool = True,
    auto_artifact: bool = True,
    artifact_domain: str | None = None,
    latex_body: str | None = None,
    include_verification: bool = False,
) -> ReconcileResult:
    """Read real state; repair only MISSING/STALE; CURRENT → 0 writes."""
    project_root = Path(root).resolve()
    completion = inspect_problem_completion(project_root, problem_id)
    result = ReconcileResult(problem_id=problem_id, completion=completion)
    if completion.error:
        result.error = completion.error
        return result

    path = find_problem_file(project_root, problem_id)
    assert path is not None
    rel = path.resolve().relative_to(project_root).as_posix()
    result.workflow_before = workflow_from_relative(rel)
    result.workflow_after = result.workflow_before

    # Fast path: fully current → zero writes
    if completion.complete and result.workflow_before == "已解决" and auto_artifact:
        art_inspect = inspect_artifact(
            project_root,
            problem_id=problem_id,
            artifact_domain=artifact_domain,
        )
        if (
            art_inspect.latex == FreshnessState.CURRENT
            and art_inspect.pdf == FreshnessState.CURRENT
        ):
            result.artifact = ArtifactReconcileResult(
                latex=FreshnessState.CURRENT,
                pdf=FreshnessState.CURRENT,
                latex_writes=0,
                builds=0,
                pdf_replaces=0,
                paths=art_inspect.paths,
            )
            return result

    changed: list[str] = []

    if (
        completion.complete
        and math_self_check_ok
        and auto_close
        and result.workflow_before == "研究中"
    ):
        v = validate_file(path, root=project_root)
        if v.summary.errors == 0:
            move = move_problem_to_workflow(
                project_root,
                problem_id,
                target_workflow="已解决",
            )
            result.workflow_move = move
            if move.error:
                result.error = move.error
                return result
            if move.moved:
                result.counters.workflow_moves = 1
                changed.append("problem")
            result.workflow_after = move.workflow_after
        else:
            result.error = "Problem Validator FAIL; archive skipped"
            return result
    elif completion.complete and not auto_close and result.workflow_before == "研究中":
        result.skipped_archive = True

    wf = result.workflow_after
    if completion.complete and auto_artifact and wf == "已解决":
        art = reconcile_artifact(
            project_root,
            problem_id=problem_id,
            artifact_domain=artifact_domain,
            latex_body=latex_body,
            auto_artifact=True,
        )
        result.artifact = art
        result.counters.latex_writes = art.latex_writes
        result.counters.builds = art.builds
        result.counters.pdf_replaces = art.pdf_replaces
    elif completion.complete and not auto_artifact:
        result.artifact = ArtifactReconcileResult(
            latex=FreshnessState.SKIPPED,
            pdf=FreshnessState.SKIPPED,
        )
    else:
        result.artifact = ArtifactReconcileResult(
            latex=FreshnessState.NOT_APPLICABLE,
            pdf=FreshnessState.NOT_APPLICABLE,
        )

    did_work = bool(
        result.counters.workflow_moves
        or result.counters.latex_writes
        or result.counters.builds
        or result.counters.pdf_replaces
    )
    if did_work:
        fin_changed = changed or ["problem"]
        result.finalize = finalize(
            root=project_root,
            changed=fin_changed,
            include_verification=include_verification,
        )
        if result.finalize.workspace_sync_performed:
            result.counters.workspace_syncs = 1

    return result


def reconcile_problem_op(
    root: Path | str,
    *,
    problem_id: str,
    math_self_check_ok: bool = True,
    auto_close: bool = True,
    auto_artifact: bool = True,
    artifact_domain: str | None = None,
    latex_body: str | None = None,
    include_verification: bool = False,
) -> ReconcileResult:
    return reconcile_problem(
        root,
        problem_id=problem_id,
        math_self_check_ok=math_self_check_ok,
        auto_close=auto_close,
        auto_artifact=auto_artifact,
        artifact_domain=artifact_domain,
        latex_body=latex_body,
        include_verification=include_verification,
    )
