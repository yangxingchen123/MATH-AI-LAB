"""Runtime models for MATH-AI-LAB Verification Contract."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class VerificationStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


class FailureCategory(str, Enum):
    """Verification failure category — not Mathematical Error Mode."""

    SOURCE_INVALID = "SOURCE_INVALID"
    GENERATED_STALE = "GENERATED_STALE"
    WORKSPACE_INVALID = "WORKSPACE_INVALID"
    TEST_FAILURE = "TEST_FAILURE"
    TOOLCHAIN_MISSING = "TOOLCHAIN_MISSING"
    LATEX_FAILURE = "LATEX_FAILURE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


_SEVERITY_RANK: dict[VerificationStatus, int] = {
    VerificationStatus.SKIPPED: 0,
    VerificationStatus.PASS: 1,
    VerificationStatus.PASS_WITH_WARNINGS: 2,
    VerificationStatus.BLOCKED: 3,
    VerificationStatus.FAIL: 4,
}


def aggregate_status(statuses: list[VerificationStatus]) -> VerificationStatus:
    if not statuses:
        return VerificationStatus.PASS
    return max(statuses, key=lambda status: _SEVERITY_RANK[status])


@dataclass(frozen=True)
class VerificationCheckResult:
    name: str
    status: VerificationStatus
    category: FailureCategory | None = None
    summary: str = ""
    details: str = ""
    duration_seconds: float = 0.0
    suggested_action: str | None = None
    layer: str = ""


@dataclass(frozen=True)
class VerificationRunResult:
    profile: str
    checks: tuple[VerificationCheckResult, ...]
    overall_status: VerificationStatus
    duration_seconds: float
    environment: Mapping[str, str] | None = None
