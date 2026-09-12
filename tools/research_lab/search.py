"""Blind greedy search for a sum-free subset of {1,...,n}.

This module may import `is_sum_free` only. It must not consult the closed-form
bound or the named constructions. Tests treat recovering ceil(n/2) as a hidden
known-result check, not a novelty claim.
"""

from __future__ import annotations

from .evaluators.sum_free import is_sum_free


def greedy_sum_free(n: int) -> set[int]:
    if n < 0:
        raise ValueError("n must be non-negative")
    chosen: set[int] = set()
    for value in range(n, 0, -1):
        trial = chosen | {value}
        if is_sum_free(trial):
            chosen = trial
    return chosen
