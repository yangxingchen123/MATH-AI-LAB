"""Problem Metadata Validator for Frozen Problem Schema v1."""

from .constants import VALIDATOR_VERSION
from .discovery import DiscoveryError, resolve_project_root
from .models import ProblemDocument, ValidationIssue, ValidationResult, ValidationSummary
from .validator import focus_view, validate_file, validate_project

__all__ = [
    "VALIDATOR_VERSION",
    "DiscoveryError",
    "ProblemDocument",
    "ValidationIssue",
    "ValidationResult",
    "ValidationSummary",
    "focus_view",
    "resolve_project_root",
    "validate_file",
    "validate_project",
]
__version__ = VALIDATOR_VERSION
