"""Object-level validation rules for Frozen Attempt Schema v1."""

from __future__ import annotations

import re
from typing import Any

from tools.problem_validator.models import ProblemDocument

from .constants import (
    ASSISTANCE_VALUES,
    FROZEN_FIELDS,
    ID_PATTERN,
    OUTCOME_VALUES,
    PROBLEM_ID_PATTERN,
    REQUIRED_FIELDS,
    RESERVED_ATTEMPT_ID,
    SCHEMA_VERSION,
)
from .models import AttemptDocument, Severity, ValidationIssue
from .rules_temporal import validate_temporal_field, validate_temporal_string


def _issue(
    rule_id: str,
    message: str,
    doc: AttemptDocument,
    *,
    field: str | None = None,
    severity: Severity = Severity.ERROR,
    target_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        severity=severity,
        rule_id=rule_id,
        message=message,
        file=doc.relative_path,
        object_id=doc.object_id,
        field=field,
        target_id=target_id,
        details=details or {},
    )


def validate_base(doc: AttemptDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    data = doc.data

    for key in sorted(data.keys(), key=str):
        if key not in FROZEN_FIELDS:
            issues.append(
                _issue(
                    "A-FIELD-E001",
                    f"Unknown metadata field: {key}",
                    doc,
                    field=str(key),
                )
            )

    for field in sorted(REQUIRED_FIELDS):
        if field not in data:
            issues.append(
                _issue(
                    "A-BASE-E030",
                    f"Required field missing: {field}.",
                    doc,
                    field=field,
                )
            )

    if "schema_version" in data:
        sv = data["schema_version"]
        if not isinstance(sv, int) or isinstance(sv, bool) or sv != SCHEMA_VERSION:
            issues.append(
                _issue(
                    "A-BASE-E002",
                    f"schema_version must be integer {SCHEMA_VERSION}, got {sv!r}.",
                    doc,
                    field="schema_version",
                )
            )

    if "id" in data:
        aid = data["id"]
        if not isinstance(aid, str) or re.fullmatch(ID_PATTERN, aid) is None:
            issues.append(
                _issue(
                    "A-BASE-E010",
                    f"Invalid Attempt ID: {aid!r}. Expected pattern {ID_PATTERN}.",
                    doc,
                    field="id",
                )
            )
        else:
            doc.object_id = aid
            if aid == RESERVED_ATTEMPT_ID:
                issues.append(
                    _issue(
                        "A-BASE-E011",
                        "Reserved ID A000000 cannot be used for a real Attempt record.",
                        doc,
                        field="id",
                    )
                )

    if "type" in data:
        if data["type"] != "attempt":
            issues.append(
                _issue(
                    "A-BASE-E021",
                    f"type must be 'attempt', got {data['type']!r}.",
                    doc,
                    field="type",
                )
            )

    if "outcome" in data:
        outcome = data["outcome"]
        if not isinstance(outcome, str) or outcome not in OUTCOME_VALUES:
            issues.append(
                _issue(
                    "A-OUT-E001",
                    f"outcome must be one of {sorted(OUTCOME_VALUES)}, got {outcome!r}.",
                    doc,
                    field="outcome",
                )
            )

    if "assistance" in data:
        assistance = data["assistance"]
        if not isinstance(assistance, str) or assistance not in ASSISTANCE_VALUES:
            issues.append(
                _issue(
                    "A-ASST-E001",
                    f"assistance must be one of {sorted(ASSISTANCE_VALUES)}, got {assistance!r}.",
                    doc,
                    field="assistance",
                )
            )

    if "attempted_at" in data:
        issues.extend(
            validate_temporal_field(doc, value=data["attempted_at"], field="attempted_at")
        )

    if "corrections" in data:
        issues.extend(validate_corrections(doc))

    return issues


def validate_corrections(doc: AttemptDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    corrections = doc.data.get("corrections")
    if corrections is None:
        return issues

    if not isinstance(corrections, list) or len(corrections) == 0:
        issues.append(
            _issue(
                "A-CORR-E001",
                "corrections must be a non-empty list when present.",
                doc,
                field="corrections",
            )
        )
        return issues

    allowed_keys = {"at", "note"}
    for index, item in enumerate(corrections):
        field_prefix = f"corrections[{index}]"
        if not isinstance(item, dict):
            issues.append(
                _issue(
                    "A-CORR-E002",
                    f"{field_prefix} must be a mapping.",
                    doc,
                    field=field_prefix,
                )
            )
            continue

        extra = set(item.keys()) - allowed_keys
        missing = allowed_keys - set(item.keys())
        if extra:
            issues.append(
                _issue(
                    "A-CORR-E003",
                    f"{field_prefix} has unknown keys: {sorted(extra)}.",
                    doc,
                    field=field_prefix,
                )
            )
        if missing:
            issues.append(
                _issue(
                    "A-CORR-E004",
                    f"{field_prefix} missing required keys: {sorted(missing)}.",
                    doc,
                    field=field_prefix,
                )
            )

        if "at" in item:
            at_field = f"{field_prefix}.at"
            issues.extend(
                validate_temporal_field(doc, value=item["at"], field=at_field)
            )

        if "note" in item:
            note = item["note"]
            if not isinstance(note, str) or not note.strip():
                issues.append(
                    _issue(
                        "A-CORR-E005",
                        f"{field_prefix}.note must be a non-empty string after trim.",
                        doc,
                        field=f"{field_prefix}.note",
                    )
                )

    return issues


def validate_unique_ids(documents: list[AttemptDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    by_id: dict[str, list[AttemptDocument]] = {}
    for doc in documents:
        if doc.object_id:
            by_id.setdefault(doc.object_id, []).append(doc)
    for aid, docs in sorted(by_id.items()):
        if len(docs) < 2:
            continue
        files = [d.relative_path for d in docs]
        for doc in docs:
            issues.append(
                _issue(
                    "A-ID-E001",
                    f"Duplicate Attempt ID {aid}: {files}",
                    doc,
                    field="id",
                    details={"files": files},
                )
            )
    return issues


def _problem_parts(problem_doc: ProblemDocument) -> list[str] | None:
    parts = problem_doc.data.get("parts")
    if parts is None:
        return None
    if not isinstance(parts, list):
        return None
    tokens: list[str] = []
    for item in parts:
        if isinstance(item, str) and item.strip():
            tokens.append(item.strip())
    return tokens if tokens else None


def validate_problem_relation(
    doc: AttemptDocument,
    *,
    problem_registry: dict[str, ProblemDocument] | None,
    problem_healthy: bool,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    data = doc.data

    if "problem" not in data:
        return issues

    problem_id = data["problem"]
    if not isinstance(problem_id, str) or re.fullmatch(PROBLEM_ID_PATTERN, problem_id) is None:
        issues.append(
            _issue(
                "A-PROB-E001",
                f"Invalid Problem ID: {problem_id!r}. Expected pattern {PROBLEM_ID_PATTERN}.",
                doc,
                field="problem",
                target_id=str(problem_id) if problem_id is not None else None,
            )
        )
        return issues

    if not problem_healthy:
        return issues

    if problem_registry is None:
        return issues

    target = problem_registry.get(problem_id)
    if target is None:
        issues.append(
            _issue(
                "A-PROB-E002",
                f"Unknown Problem reference: {problem_id}.",
                doc,
                field="problem",
                target_id=problem_id,
            )
        )
        return issues

    if "part" not in data:
        return issues

    part = data["part"]
    parts_list = _problem_parts(target)

    if not isinstance(part, str) or not part.strip():
        issues.append(
            _issue(
                "A-PART-E001",
                f"part must be a single scalar anchor string, got {part!r}.",
                doc,
                field="part",
            )
        )
        return issues

    anchor = part.strip()
    if parts_list is None:
        issues.append(
            _issue(
                "A-PART-E003",
                f"Problem {problem_id} has no parts but part={anchor!r} is present.",
                doc,
                field="part",
                target_id=problem_id,
            )
        )
        return issues

    if anchor not in parts_list:
        issues.append(
            _issue(
                "A-PART-E002",
                f"Unknown part reference {anchor!r} for Problem {problem_id}.",
                doc,
                field="part",
                target_id=problem_id,
            )
        )

    return issues


def validate_part_shape(doc: AttemptDocument) -> list[ValidationIssue]:
    """Reject list/mapping part values before relation checks."""
    if "part" not in doc.data:
        return []
    part = doc.data["part"]
    if isinstance(part, (list, dict)):
        return [
            _issue(
                "A-PART-E001",
                f"part must be a single scalar anchor, got {type(part).__name__}.",
                doc,
                field="part",
            )
        ]
    return []
