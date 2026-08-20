"""Method Metadata Validator for Frozen Method Schema v1."""

from .constants import VALIDATOR_VERSION
from .discovery import DiscoveryError, resolve_project_root
from .models import MethodDocument, ValidationIssue, ValidationResult, ValidationSummary
from .validator import focus_view, validate_file, validate_project

__all__ = [
    "VALIDATOR_VERSION",
    "DiscoveryError",
    "MethodDocument",
    "ValidationIssue",
    "ValidationResult",
    "ValidationSummary",
    "focus_view",
    "resolve_project_root",
    "validate_file",
    "validate_project",
]
__version__ = VALIDATOR_VERSION
