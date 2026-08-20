"""Aggregation and precedence tests for verification runtime models."""

from __future__ import annotations

from tools.verification.models import (
    FailureCategory,
    VerificationCheckResult,
    VerificationRunResult,
    VerificationStatus,
    aggregate_status,
)


def _check(name: str, status: VerificationStatus) -> VerificationCheckResult:
    return VerificationCheckResult(name=name, status=status)


def test_aggregate_all_pass() -> None:
    assert aggregate_status([VerificationStatus.PASS, VerificationStatus.PASS]) == VerificationStatus.PASS


def test_aggregate_warnings() -> None:
    assert (
        aggregate_status([VerificationStatus.PASS, VerificationStatus.PASS_WITH_WARNINGS])
        == VerificationStatus.PASS_WITH_WARNINGS
    )


def test_aggregate_blocked() -> None:
    assert (
        aggregate_status([VerificationStatus.PASS, VerificationStatus.BLOCKED])
        == VerificationStatus.BLOCKED
    )


def test_aggregate_fail() -> None:
    assert aggregate_status([VerificationStatus.PASS, VerificationStatus.FAIL]) == VerificationStatus.FAIL


def test_fail_outranks_blocked() -> None:
    assert (
        aggregate_status([VerificationStatus.BLOCKED, VerificationStatus.FAIL])
        == VerificationStatus.FAIL
    )


def test_blocked_outranks_warning() -> None:
    assert (
        aggregate_status([VerificationStatus.PASS_WITH_WARNINGS, VerificationStatus.BLOCKED])
        == VerificationStatus.BLOCKED
    )


def test_skipped_does_not_raise_severity() -> None:
    assert (
        aggregate_status([VerificationStatus.PASS, VerificationStatus.SKIPPED])
        == VerificationStatus.PASS
    )


def test_run_result_preserves_check_order() -> None:
    checks = (_check("A", VerificationStatus.PASS), _check("B", VerificationStatus.FAIL))
    run = VerificationRunResult(
        profile="core",
        checks=checks,
        overall_status=aggregate_status([c.status for c in checks]),
        duration_seconds=1.0,
    )
    assert [c.name for c in run.checks] == ["A", "B"]
    assert run.overall_status == VerificationStatus.FAIL


def test_pass_allows_none_category() -> None:
    result = VerificationCheckResult(name="x", status=VerificationStatus.PASS)
    assert result.category is None


def test_failure_category_is_not_error_mode() -> None:
    assert FailureCategory.SOURCE_INVALID.value == "SOURCE_INVALID"
    assert not hasattr(FailureCategory, "EM_ID")
