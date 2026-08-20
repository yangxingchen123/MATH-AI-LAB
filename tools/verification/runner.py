"""Dependency-aware verification runner. Not a generic DAG engine."""

from __future__ import annotations

import time
from pathlib import Path

from tools.knowledge_validator import resolve_project_root

from .checks import (
    CheckHooks,
    blocked_derived,
    collect_environment,
    run_attempt_validator,
    run_knowledge_validator,
    run_latex_smoke,
    run_method_validator,
    run_problem_validator,
    run_pytest_check,
    run_workspace_check_adapter,
    run_workspace_indexer_check,
)
from .models import (
    FailureCategory,
    VerificationCheckResult,
    VerificationRunResult,
    VerificationStatus,
    aggregate_status,
)
from .profiles import (
    PROFILE_ALL,
    PROFILE_CORE,
    PROFILE_LATEX_SMOKE,
    PROFILES_REQUIRING_LATEX_PROJECT,
)


class VerificationUsageError(ValueError):
    """Invalid profile invocation."""


def _safe(name: str, layer: str, fn):
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 — verification must not crash the remaining profile
        return wrap_internal_error(name, layer, exc)


def _source_ok(checks: list[VerificationCheckResult]) -> bool:
    return all(item.status in (VerificationStatus.PASS, VerificationStatus.PASS_WITH_WARNINGS) for item in checks)


def _run_source(root: Path, hooks: CheckHooks) -> tuple[list[VerificationCheckResult], bool]:
    knowledge_fn = hooks.knowledge or run_knowledge_validator
    problem_fn = hooks.problem or run_problem_validator
    attempt_fn = hooks.attempt or run_attempt_validator
    method_fn = hooks.method or run_method_validator

    k_check, k_raw = knowledge_fn(root)
    p_check, p_raw = problem_fn(root, k_raw)
    a_check, _a_raw = attempt_fn(root, p_raw)
    m_check, _m_raw = method_fn(root, k_raw)
    checks = [k_check, p_check, a_check, m_check]
    return checks, _source_ok(checks)


def _run_derived(root: Path, hooks: CheckHooks, *, source_ok: bool) -> list[VerificationCheckResult]:
    if not source_ok:
        return [
            blocked_derived("Workspace Indexer"),
            blocked_derived("Workspace Check"),
        ]
    indexer_fn = hooks.workspace_indexer or run_workspace_indexer_check
    check_fn = hooks.workspace_check or run_workspace_check_adapter
    return [indexer_fn(root), check_fn(root)]


def run_verification(
    profile: str,
    *,
    root: Path | None = None,
    latex_project: str | None = None,
    verbose: bool = False,
    hooks: CheckHooks | None = None,
) -> VerificationRunResult:
    start = time.perf_counter()
    hooks = hooks or CheckHooks()
    project_root = resolve_project_root(root)

    if profile not in {PROFILE_CORE, PROFILE_LATEX_SMOKE, PROFILE_ALL}:
        raise VerificationUsageError(f"Unknown profile: {profile}")
    if profile in PROFILES_REQUIRING_LATEX_PROJECT and not latex_project:
        raise VerificationUsageError(f"Profile {profile!r} requires a LaTeX project path.")

    checks: list[VerificationCheckResult] = []

    if profile in {PROFILE_CORE, PROFILE_ALL}:
        source_checks, source_ok = _run_source(project_root, hooks)
        checks.extend(source_checks)
        checks.extend(_run_derived(project_root, hooks, source_ok=source_ok))
        pytest_fn = hooks.pytest or (lambda path: run_pytest_check(path))
        checks.append(pytest_fn(project_root))

    if profile in {PROFILE_LATEX_SMOKE, PROFILE_ALL}:
        assert latex_project is not None
        latex_fn = hooks.latex or (lambda path, proj: run_latex_smoke(path, proj))
        checks.append(latex_fn(project_root, latex_project))

    env = collect_environment(project_root, latex_project=latex_project) if verbose else None
    overall = aggregate_status([item.status for item in checks])
    return VerificationRunResult(
        profile=profile,
        checks=tuple(checks),
        overall_status=overall,
        duration_seconds=time.perf_counter() - start,
        environment=env,
    )


def wrap_internal_error(name: str, layer: str, exc: BaseException) -> VerificationCheckResult:
    return VerificationCheckResult(
        name=name,
        status=VerificationStatus.FAIL,
        category=FailureCategory.INTERNAL_ERROR,
        summary=str(exc),
        layer=layer,
    )
