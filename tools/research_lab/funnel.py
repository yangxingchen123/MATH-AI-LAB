"""C0 cheap-candidate funnel. Deterministic; no LLM; clusters failures and stops on stall."""

from __future__ import annotations

from collections import Counter

from .evaluators import dispatch as dispatch_evaluator
from .ledger import Budget, budget_for_layer
from .registry import validate_record
from .search import greedy_sum_free

LAYERS: tuple[str, ...] = ("C0", "C1", "C2", "C3", "C4", "C5")


def cheap_candidates(n: int, *, limit: int = 16) -> list[set[int]]:
    found: list[set[int]] = []
    seen: set[frozenset[int]] = set()

    def add(values: set[int]) -> None:
        key = frozenset(values)
        if key in seen or len(found) >= limit:
            return
        seen.add(key)
        found.append(set(values))

    add(set())
    if n >= 1:
        add({n})
    if n >= 3:
        add({1, 2, 3})
    add(greedy_sum_free(n))
    for k in range(1, min(n, 4) + 1):
        add({k})
    if n >= 2:
        add(set(range(max(1, n - 2), n + 1)))
    width = min(n, 12) if n else 0
    if width:
        mask = 0
        max_mask = 1 << width
        while len(found) < limit and mask < max_mask:
            values = {i + 1 for i in range(n) if mask & (1 << (i % width))}
            add(values)
            mask += 1
    return found[:limit]


def run_funnel(
    problem: dict,
    *,
    n: int = 10,
    limit: int = 16,
    stall_rounds: int = 4,
    layer: str = "C0",
    budget: Budget | None = None,
) -> dict:
    del budget
    errors = validate_record(problem)
    if errors:
        return {
            "ok": False,
            "errors": errors,
            "usd": 0.0,
            "writes_source": False,
            "core_impact": False,
        }
    if layer not in LAYERS:
        return {
            "ok": False,
            "errors": [f"unknown funnel layer: {layer}"],
            "usd": 0.0,
            "writes_source": False,
            "core_impact": False,
        }
    evaluator = str(problem.get("evaluator") or "")
    results: list[dict] = []
    best = -1
    stalled = 0
    stopped = "completed"
    for candidate in cheap_candidates(n, limit=limit):
        try:
            report = dispatch_evaluator(evaluator, n=n, values=candidate)
        except KeyError:
            return {
                "ok": False,
                "errors": [f"unknown evaluator: {evaluator}"],
                "usd": 0.0,
                "writes_source": False,
                "core_impact": False,
            }
        row = {
            "candidate": sorted(candidate),
            "valid": bool(report.get("valid")),
            "optimal": bool(report.get("optimal")),
            "reason": report.get("reason"),
            "size": report.get("size"),
        }
        results.append(row)
        size = int(report.get("size") or 0) if report.get("valid") else -1
        if size > best:
            best = size
            stalled = 0
        else:
            stalled += 1
            if stalled >= stall_rounds:
                stopped = "stalled"
                break
    verified = sum(1 for item in results if item["valid"])
    optimal = sum(1 for item in results if item["optimal"])
    clusters = dict(Counter(str(item.get("reason") or "unknown") for item in results))
    may_promote = verified > 0 and layer == "C0"
    return {
        "ok": optimal > 0 or verified > 0,
        "problem_id": problem.get("id"),
        "layer": layer,
        "n": n,
        "attempts": len(results),
        "verified_successes": verified,
        "optimal_successes": optimal,
        "best_size": best if best >= 0 else None,
        "clusters": clusters,
        "stopped": stopped,
        "usd": 0.0,
        "cost_adjusted_success": None,
        "may_promote_to": "C1" if may_promote else None,
        "writes_source": False,
        "core_impact": False,
        "results": results,
        "budget_cap_usd": budget_for_layer(layer).hard_limit_usd,
        "note": "Zero-USD deterministic funnel. cost_adjusted_success is undefined at 0 USD.",
        "errors": [],
    }
