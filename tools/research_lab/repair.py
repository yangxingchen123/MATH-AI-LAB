"""Local repair. May change the candidate, never the statement."""

from __future__ import annotations

from .evaluators import dispatch as dispatch_evaluator
from .evidence import statement_hash
from .protocol import load_protocol

DEFAULT_UNREPAIRABLE: frozenset[str] = frozenset({"out_of_universe"})


def unrepairable_reasons(protocol: dict | None = None) -> frozenset[str]:
    contract = protocol or load_protocol()
    raw = contract.get("unrepairable_reasons") or list(DEFAULT_UNREPAIRABLE)
    return frozenset(str(item) for item in raw)


def local_repair(
    problem: dict,
    *,
    n: int,
    failed_reason: str,
    values: set[int] | None = None,
) -> dict:
    before = statement_hash(problem)
    banned = unrepairable_reasons()
    if failed_reason in banned:
        return {
            "ok": False,
            "errors": ["unrepairable_no_retry"],
            "mutated_statement": False,
            "statement_hash": before,
            "usd": 0.0,
            "writes_source": False,
            "core_impact": False,
        }
    evaluator = str(problem.get("evaluator") or "")
    try:
        report = dispatch_evaluator(evaluator, n=n, values=values)
    except KeyError:
        return {
            "ok": False,
            "errors": [f"unknown evaluator: {evaluator}"],
            "mutated_statement": False,
            "statement_hash": before,
            "usd": 0.0,
            "writes_source": False,
            "core_impact": False,
        }
    after = statement_hash(problem)
    mutated = before != after
    errors = ["statement_mutated"] if mutated else []
    return {
        "ok": bool(report.get("valid")) and not mutated,
        "errors": errors,
        "mutated_statement": mutated,
        "statement_hash": after,
        "evaluator_report": report,
        "usd": 0.0,
        "writes_source": False,
        "core_impact": False,
        "note": "Repair retries a candidate. It must not edit the theorem statement.",
    }
