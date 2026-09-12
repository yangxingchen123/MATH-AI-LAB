"""One-shot read-only verification for the v2.2-lab Pilot.

Never writes production Source. Missing lake is DEGRADED, never a Core failure.
"""

from __future__ import annotations

import yaml

from tools.lean_formalization.build import run_lake_build
from tools.lean_formalization.correspondence import load_table, undeclared_theorems, validate_table
from tools.lean_formalization.scan import scan_lean_tree

from .constants import CONTRACT_VERSION, CORRESPONDENCE_PATH, LEAN_ROOT, PROBLEM_REGISTRY
from .evaluators.sum_free import (
    enumerative_bound_range,
    evaluate_candidate,
    max_sum_free_size,
    odds_construction,
    upper_half_construction,
)
from .registry import load_record, validate_record
from .search import greedy_sum_free

VERIFY_MAX_N = 12
REQUIRED_CORRESPONDENCE_IDS: tuple[str, ...] = (
    "ANL-001",
    "DISC-003",
    "DISC-004",
    "DISC-005",
    "DISC-006",
)


def verify() -> dict:
    checks = [
        _problem_registry(),
        _known_constructions(),
        _exhaustive_bound(),
        _correspondence(),
        _lean_scan(),
        _lake_build(),
    ]
    python_failed = any(
        item["status"] == "FAIL" and item["name"] != "lake_build" for item in checks
    )
    lake = next(item for item in checks if item["name"] == "lake_build")
    if python_failed or lake["status"] == "FAIL":
        status = "FAIL"
    elif lake["status"] == "DEGRADED":
        status = "DEGRADED"
    else:
        status = "PASS"
    return {
        "contract_version": CONTRACT_VERSION,
        "status": status,
        "core_impact": False,
        "pilot": True,
        "checks": checks,
        "note": "Sidecar. Does not write Source. Does not claim 四大 or v2.2 VERIFIED.",
    }


def _check(name: str, ok: bool, detail: object, *, status: str | None = None) -> dict:
    resolved = status or ("PASS" if ok else "FAIL")
    return {"name": name, "status": resolved, "detail": str(detail)}


def _problem_registry() -> dict:
    if not PROBLEM_REGISTRY.is_file():
        return _check("problem_registry", False, f"missing {PROBLEM_REGISTRY}")
    record = load_record(PROBLEM_REGISTRY)
    errors = validate_record(record)
    decls = record.get("lean_decls") or []
    has_bound = "MathAILab.Research.sum_free_length_le" in decls
    ok = errors == [] and has_bound
    detail = errors or "PROB-SF-001 valid; sum_free_length_le listed"
    return _check("problem_registry", ok, detail)


def _known_constructions() -> dict:
    for n in range(0, VERIFY_MAX_N + 1):
        bound = max_sum_free_size(n)
        for candidate in (
            greedy_sum_free(n),
            odds_construction(n),
            upper_half_construction(n),
        ):
            report = evaluate_candidate(n, candidate)
            if not report.get("valid") or not report.get("optimal"):
                return _check(
                    "known_constructions",
                    False,
                    f"n={n} candidate={sorted(candidate)} report={report}",
                )
            if len(candidate) != bound:
                return _check("known_constructions", False, f"n={n} size {len(candidate)} != {bound}")
    return _check(
        "known_constructions",
        True,
        f"greedy/odds/upper-half optimal for n=0..{VERIFY_MAX_N}",
    )


def _exhaustive_bound() -> dict:
    ok = enumerative_bound_range(VERIFY_MAX_N)
    return _check(
        "exhaustive_bound",
        ok,
        f"every sum-free subset of {{1..n}} has size <= ceil(n/2) for n=0..{VERIFY_MAX_N}",
    )


def _correspondence() -> dict:
    if not CORRESPONDENCE_PATH.is_file():
        return _check("correspondence", False, "missing correspondence.yaml")
    table = load_table(CORRESPONDENCE_PATH)
    result = validate_table(table, LEAN_ROOT)
    ids = {item.get("id") for item in table if isinstance(item, dict)}
    missing_ids = [item for item in REQUIRED_CORRESPONDENCE_IDS if item not in ids]
    undeclared = undeclared_theorems(LEAN_ROOT, table)
    ok = result.ok and not missing_ids and not undeclared
    detail = {
        "validate_ok": result.ok,
        "errors": result.errors,
        "missing_ids": missing_ids,
        "undeclared": undeclared,
    }
    return _check("correspondence", ok, detail)


def _lean_scan() -> dict:
    hits = scan_lean_tree(LEAN_ROOT)
    production = [
        hit
        for hit in hits
        if "/tests/" not in hit.path.replace("\\", "/")
        and "fixtures" not in hit.path.replace("\\", "/")
    ]
    detail = [
        {"path": hit.path, "kind": hit.kind, "line": hit.line} for hit in production
    ]
    return _check("lean_scan", production == [], detail or "no sorry/admit/axiom")


def _lake_build() -> dict:
    result = run_lake_build(LEAN_ROOT)
    if result.status == "SUCCEEDED":
        status = "PASS"
    elif result.status == "DEGRADED":
        status = "DEGRADED"
    else:
        status = "FAIL"
    log = result.log.strip().splitlines()
    tail = "\n".join(log[-12:]) if log else result.status
    return _check("lake_build", status == "PASS", tail, status=status)
