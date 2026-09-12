"""Deterministic sum-free subset evaluator (known bound, not a novelty claim)."""

from __future__ import annotations


def first_sum_witness(values: set[int]) -> tuple[int, int, int] | None:
    items = tuple(values)
    for i, left in enumerate(items):
        for right in items[i:]:
            total = left + right
            if total in values:
                return (left, right, total)
    return None


def is_sum_free(values: set[int]) -> bool:
    return first_sum_witness(values) is None


def max_sum_free_size(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    return (n + 1) // 2


def upper_half_construction(n: int) -> set[int]:
    if n < 0:
        raise ValueError("n must be non-negative")
    start = (n + 2) // 2
    return set(range(start, n + 1))


def odds_construction(n: int) -> set[int]:
    if n < 0:
        raise ValueError("n must be non-negative")
    return {k for k in range(1, n + 1) if k % 2 == 1}


def enumerative_bound_holds(n: int) -> bool:
    """Every sum-free subset of {1..n} has size at most ceil(n/2). Independent of Lean."""
    if n < 0:
        raise ValueError("n must be non-negative")
    bound = max_sum_free_size(n)
    for mask in range(1 << n):
        values = {i + 1 for i in range(n) if mask & (1 << i)}
        if is_sum_free(values) and len(values) > bound:
            return False
    return True


def enumerative_bound_range(max_n: int) -> bool:
    if max_n < 0:
        raise ValueError("max_n must be non-negative")
    return all(enumerative_bound_holds(n) for n in range(0, max_n + 1))


def evaluate_candidate(n: int, values: set[int]) -> dict:
    universe = set(range(1, n + 1))
    if not values.issubset(universe):
        return {"valid": False, "reason": "out_of_universe", "size": len(values)}
    if not is_sum_free(values):
        witness = first_sum_witness(values)
        return {
            "valid": False,
            "reason": "not_sum_free",
            "size": len(values),
            "witness": list(witness) if witness else None,
        }
    size = len(values)
    bound = max_sum_free_size(n)
    return {
        "valid": True,
        "reason": "sum_free",
        "size": size,
        "bound": bound,
        "optimal": size == bound,
    }
