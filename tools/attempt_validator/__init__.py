"""Attempt Metadata Validator for Frozen Attempt Schema v1."""

from .constants import VALIDATOR_VERSION
from .discovery import DiscoveryError, resolve_project_root
from .ledger import allocate_next_attempt_id, append_attempt_to_ledger
from .models import AttemptDocument, ValidationIssue, ValidationResult, ValidationSummary
from .validator import focus_view, validate_file, validate_project

__all__ = [
    "VALIDATOR_VERSION",
    "AttemptDocument",
    "DiscoveryError",
    "ValidationIssue",
    "ValidationResult",
    "ValidationSummary",
    "allocate_next_attempt_id",
    "append_attempt_to_ledger",
    "focus_view",
    "resolve_project_root",
    "validate_file",
    "validate_project",
]
__version__ = VALIDATOR_VERSION
