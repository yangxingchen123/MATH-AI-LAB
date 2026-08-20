"""Frozen Temporal Contract validation (Attempt Schema v1 §8.10)."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from .models import AttemptDocument, Severity, ValidationIssue

FORM_A_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})([+-]\d{2}:\d{2})$")
FORM_B_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})$")
OFFSET_RE = re.compile(r"^[+-]\d{2}:\d{2}$")


def _valid_calendar_date(date_part: str) -> bool:
    try:
        datetime.strptime(date_part, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def validate_temporal_string(value: Any) -> list[ValidationIssue]:
    """Return issues for a single temporal scalar (attempted_at or corrections[].at)."""
    if not isinstance(value, str):
        return [
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="A-TEMP-E001",
                message=(
                    f"Temporal value must be a quoted string scalar, got {type(value).__name__}."
                ),
            )
        ]

    text = value
    match_b = FORM_B_RE.fullmatch(text)
    if match_b:
        if not _valid_calendar_date(match_b.group(1)):
            return [
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="A-TEMP-E002",
                    message=f"Invalid calendar date in temporal string: {text!r}.",
                )
            ]
        return []

    match_a = FORM_A_RE.fullmatch(text)
    if match_a:
        date_part, hour_s, minute_s, offset = match_a.groups()
        if not _valid_calendar_date(date_part):
            return [
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="A-TEMP-E002",
                    message=f"Invalid calendar date in temporal string: {text!r}.",
                )
            ]
        hour = int(hour_s)
        minute = int(minute_s)
        if hour > 23 or minute > 59:
            return [
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="A-TEMP-E002",
                    message=f"Invalid hour/minute in temporal string: {text!r}.",
                )
            ]
        if not OFFSET_RE.fullmatch(offset):
            return [
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="A-TEMP-E002",
                    message=f"Invalid UTC offset in temporal string: {text!r}.",
                )
            ]
        off_h, off_m = offset[1:3], offset[4:6]
        if int(off_h) > 23 or int(off_m) > 59:
            return [
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="A-TEMP-E002",
                    message=f"Invalid UTC offset in temporal string: {text!r}.",
                )
            ]
        return []

    return [
        ValidationIssue(
            severity=Severity.ERROR,
            rule_id="A-TEMP-E002",
            message=(
                f"Invalid temporal string: {text!r}. "
                "Expected YYYY-MM-DD or YYYY-MM-DDTHH:MM±HH:MM."
            ),
        )
    ]


def validate_temporal_field(
    doc: AttemptDocument,
    *,
    value: Any,
    field: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for base in validate_temporal_string(value):
        issues.append(
            ValidationIssue(
                severity=base.severity,
                rule_id=base.rule_id,
                message=base.message,
                file=doc.relative_path,
                object_id=doc.object_id,
                field=field,
            )
        )
    return issues
