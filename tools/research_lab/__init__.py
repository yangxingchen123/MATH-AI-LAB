"""v2.2-lab research-lab Pilot. Candidate contract; not Frozen Schema."""

from .evaluators.sum_free import (
    evaluate_candidate,
    first_sum_witness,
    is_sum_free,
    max_sum_free_size,
    odds_construction,
    upper_half_construction,
)
from .failures import append_failure, load_failures
from .fidelity import detect_mutants, load_suite
from .inventory import scan_inventory
from .ledger import Budget, BudgetExceeded, LedgerEntry, append_entry, load_entries, spent
from .registry import STAGES, TERMINAL_STAGES, load_record, validate_record
from .search import greedy_sum_free

__all__ = [
    "Budget",
    "BudgetExceeded",
    "LedgerEntry",
    "STAGES",
    "TERMINAL_STAGES",
    "append_failure",
    "append_entry",
    "detect_mutants",
    "evaluate_candidate",
    "first_sum_witness",
    "greedy_sum_free",
    "is_sum_free",
    "load_entries",
    "load_failures",
    "load_record",
    "load_suite",
    "max_sum_free_size",
    "odds_construction",
    "scan_inventory",
    "spent",
    "upper_half_construction",
    "validate_record",
]
