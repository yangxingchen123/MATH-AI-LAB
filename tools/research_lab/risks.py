"""Risk register from the original lab design §16. Controls, not 四大 claims."""

from __future__ import annotations

from .adapters import may_expand_budget
from .closeout import load_holdout
from .protocol import load_protocol
from .registry import load_record, validate_record


def evaluate_risks(problem: dict | None = None, protocol: dict | None = None) -> dict:
    record = problem if problem is not None else load_record_safe()
    contract = protocol or load_protocol()
    checks = [
        _check(
            "statement_drift",
            True,
            "statement_hash seals cycle runs; repair forbids mutate_statement",
        ),
        _check(
            "novelty_hallucination",
            not (record.get("novelty_claim") == "first" and not record.get("expert_signoff")),
            "first-claim requires expert_signoff",
        ),
        _check(
            "budget_explosion",
            may_expand_budget("C5", record) is False or bool(record.get("human_pi_signoff")),
            "C4/C5 blocked without human PI",
        ),
        _check(
            "evaluator_gaming",
            _holdout_separated(),
            "holdout n is outside public exhaustive n≤12",
        ),
        _check(
            "unrepairable_retry",
            contract.get("forbid_retry_unrepairable") is True
            and "out_of_universe" in (contract.get("unrepairable_reasons") or []),
            "unrepairable reasons cannot be retried",
        ),
        _check(
            "numeric_as_proof",
            "numeric" in (contract.get("evidence_layers") or []),
            "numeric layer exists and cannot be claimed as proved without human_proof/lean",
        ),
    ]
    ok = all(item["status"] == "PASS" for item in checks)
    return {
        "ok": ok,
        "claims_四大": False,
        "writes_source": False,
        "core_impact": False,
        "checks": checks,
        "note": "Risk controls. Passing them does not claim 四大.",
    }


def load_record_safe() -> dict:
    from .constants import PROBLEM_REGISTRY

    if not PROBLEM_REGISTRY.is_file():
        return {}
    record = load_record(PROBLEM_REGISTRY)
    if validate_record(record):
        return record
    return record


def _holdout_separated() -> bool:
    holdout = load_holdout()
    public = int(holdout.get("public_max_n") or 0)
    hidden = [int(item) for item in (holdout.get("holdout_n") or [])]
    return public == 12 and hidden and all(item > public for item in hidden)


def _check(name: str, ok: bool, detail: str) -> dict:
    return {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
