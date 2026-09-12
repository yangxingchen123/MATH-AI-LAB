"""Registered discrete evaluators. Cycle dispatches by name; no LLM."""

from __future__ import annotations

from .sum_free import evaluate_candidate

REGISTERED: frozenset[str] = frozenset({"sum_free"})


def dispatch(name: str, *, n: int, values: set[int] | None = None) -> dict:
    if name == "sum_free":
        from ..search import greedy_sum_free

        candidate = values if values is not None else greedy_sum_free(n)
        report = evaluate_candidate(n, candidate)
        report["candidate"] = sorted(candidate)
        return report
    raise KeyError(name)
