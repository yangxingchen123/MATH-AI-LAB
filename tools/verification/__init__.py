"""Verification Contract — unified local and CI verification."""

from .models import (
    FailureCategory,
    VerificationCheckResult,
    VerificationRunResult,
    VerificationStatus,
    aggregate_status,
)
from .runner import run_verification

__all__ = [
    "FailureCategory",
    "VerificationCheckResult",
    "VerificationRunResult",
    "VerificationStatus",
    "aggregate_status",
    "run_verification",
]
