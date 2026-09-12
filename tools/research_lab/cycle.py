"""Deterministic research cycle. Dispatches registered evaluators; does not write Source."""

from __future__ import annotations

from pathlib import Path

from .evaluators import dispatch as dispatch_evaluator
from .evidence import seal_run
from .failures import append_failure
from .ledger import Budget, LedgerEntry, append_entry
from .registry import load_record, validate_record
from .transitions import allowed_transition

EVALUATABLE_STAGES: frozenset[str] = frozenset(
    {"FALSIFICATION", "CANDIDATE_SURVIVED", "PROOF_PLANNED"}
)


def run_cycle(
    problem: dict,
    *,
    n: int = 10,
    values: set[int] | None = None,
    ledger_path: Path | None = None,
    failure_path: Path | None = None,
    budget: Budget | None = None,
) -> dict:
    errors = validate_record(problem)
    if errors:
        return _halt(errors, n)
    stage = str(problem.get("stage") or "")
    if stage not in EVALUATABLE_STAGES:
        return _halt([f"stage {stage} is not evaluatable"], n)
    evaluator = problem.get("evaluator")
    try:
        report = dispatch_evaluator(str(evaluator or ""), n=n, values=values)
    except KeyError:
        return _halt([f"unknown evaluator: {evaluator}"], n)
    if ledger_path is not None and budget is not None:
        append_entry(
            ledger_path,
            LedgerEntry(
                task_id=str(problem.get("id") or "unknown"),
                stage="C0",
                model="none",
                usd=0.0,
                seconds=0.0,
                input_hash=f"{problem.get('id')}:{n}:{sorted(report.get('candidate') or [])}",
                result_status="ok" if report.get("valid") else "rejected",
            ),
            budget,
        )
    if failure_path is not None and not report.get("valid"):
        append_failure(
            failure_path,
            {
                "problem_id": problem.get("id"),
                "n": n,
                "candidate": report.get("candidate"),
                "status": "REJECTED_FALSE",
                "reason": report.get("reason"),
                "witness": report.get("witness"),
            },
        )
    payload = {
        "ok": bool(report.get("valid")),
        "problem_id": problem.get("id"),
        "stage": stage,
        "evaluator": evaluator,
        "evaluator_report": report,
        "evidence_layer": "numeric",
        "novelty_claim": problem.get("novelty_claim"),
        "writes_source": False,
        "core_impact": False,
        "usd": 0.0,
        "n": n,
        "can_advance_survived": allowed_transition(stage, "CANDIDATE_SURVIVED")
        and bool(report.get("valid")),
        "errors": [],
    }
    payload["chain"] = seal_run(problem, payload)
    return payload


def run_cycle_file(path: Path, **kwargs) -> dict:
    return run_cycle(load_record(path), **kwargs)


def _halt(errors: list[str], n: int) -> dict:
    return {
        "ok": False,
        "errors": errors,
        "writes_source": False,
        "core_impact": False,
        "usd": 0.0,
        "n": n,
    }
