"""Deterministic post-mutation finalization for Normal Operation v1."""

from __future__ import annotations

import time
from pathlib import Path

from tools.attempt_validator import validate_project as validate_attempt_project
from tools.knowledge_validator import validate_project as validate_knowledge_project
from tools.method_validator import validate_project as validate_method_project
from tools.problem_validator import validate_project as validate_problem_project
from tools.verification import run_verification
from tools.verification.profiles import PROFILE_CORE
from tools.workspace_check import run_workspace_check
from tools.workspace_indexer import check_index, sync_index
from tools.workspace_indexer.models import IndexResultKind

from .models import FinalizeResult, LayerStatus


def finalize(
    *,
    root: Path | str,
    changed: list[str] | str,
    include_verification: bool = True,
) -> FinalizeResult:
    """Run validators → workspace check-first → conditional sync → verification core."""
    started = time.perf_counter()
    project_root = Path(root).resolve()
    if isinstance(changed, str):
        changed_types = [part.strip() for part in changed.split(",") if part.strip()]
    else:
        changed_types = list(changed)

    result = FinalizeResult(changed_types=changed_types)
    knowledge_result = None
    problem_result = None

    try:
        if "knowledge" in changed_types:
            knowledge_result = validate_knowledge_project(root=project_root)
            result.validation_errors += knowledge_result.summary.errors
        if "method" in changed_types:
            method_result = validate_method_project(root=project_root, knowledge_result=knowledge_result)
            result.validation_errors += method_result.summary.errors
            if knowledge_result is None:
                knowledge_result = validate_knowledge_project(root=project_root)
        if "problem" in changed_types:
            problem_result = validate_problem_project(root=project_root, knowledge_result=knowledge_result)
            result.validation_errors += problem_result.summary.errors
            if knowledge_result is None:
                knowledge_result = validate_knowledge_project(root=project_root)
        if "attempt" in changed_types:
            attempt_result = validate_attempt_project(root=project_root, problem_result=problem_result)
            result.validation_errors += attempt_result.summary.errors
            if problem_result is None and knowledge_result is None:
                knowledge_result = validate_knowledge_project(root=project_root)
                problem_result = validate_problem_project(root=project_root, knowledge_result=knowledge_result)
    except Exception as exc:
        result.validation_status = LayerStatus.FAIL
        result.issues.append(str(exc))
        result.suggested_action = "Fix validation dependency errors before finalization."
        result.duration_seconds = time.perf_counter() - started
        return result

    if result.validation_errors > 0:
        result.validation_status = LayerStatus.FAIL
        result.suggested_action = "Fix Source validation errors; workspace sync skipped."
        result.duration_seconds = time.perf_counter() - started
        return result

    result.validation_status = LayerStatus.PASS if changed_types else LayerStatus.SKIPPED

    index_check = check_index(root=project_root)
    result.workspace_initial = index_check.result.value
    if index_check.result in {IndexResultKind.STALE, IndexResultKind.MISSING}:
        sync_result = sync_index(root=project_root)
        result.workspace_sync_performed = True
        result.workspace_initial = sync_result.result.value if sync_result.result != IndexResultKind.FAIL else result.workspace_initial
        index_check = check_index(root=project_root)
    result.workspace_final = index_check.result.value

    if index_check.result == IndexResultKind.FAIL:
        result.workspace_check_status = LayerStatus.BLOCKED
        result.suggested_action = "Workspace indexer failed; fix upstream validation or index build."
        result.duration_seconds = time.perf_counter() - started
        return result

    ws_check = run_workspace_check(root=project_root)
    result.workspace_errors = ws_check.error_count
    result.workspace_warnings = ws_check.warning_count
    result.workspace_check_status = (
        LayerStatus.PASS if ws_check.error_count == 0 and ws_check.warning_count == 0 else LayerStatus.FAIL
    )
    if result.workspace_check_status == LayerStatus.FAIL:
        result.suggested_action = "Fix workspace consistency errors before verification."
        result.duration_seconds = time.perf_counter() - started
        return result

    if include_verification:
        verify = run_verification(PROFILE_CORE, root=project_root)
        result.verification_status = (
            LayerStatus.PASS if verify.overall_status.value == "PASS" else LayerStatus.FAIL
        )
        if result.verification_status == LayerStatus.FAIL:
            result.suggested_action = "Run `python -m tools.verification core` and fix failing checks."
    else:
        result.verification_status = LayerStatus.SKIPPED

    result.duration_seconds = time.perf_counter() - started
    return result
