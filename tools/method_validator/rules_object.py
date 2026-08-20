"""Object-level validation rules for Frozen Method Schema v1."""

from __future__ import annotations

import re
from typing import Any

from .constants import (
    ALLOWED_STATUSES,
    FROZEN_FIELDS,
    ID_PATTERN,
    KNOWLEDGE_ID_PATTERN,
    RESERVED_KNOWLEDGE_ID,
    RESERVED_METHOD_ID,
    SCHEMA_VERSION,
)
from .models import MethodDocument, Severity, ValidationIssue


def _issue(
    rule_id: str,
    message: str,
    doc: MethodDocument,
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


def validate_base(doc: MethodDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    data = doc.data

    for key in sorted(data.keys(), key=str):
        if key not in FROZEN_FIELDS:
            issues.append(
                _issue(
                    "M-FIELD-E001",
                    f"Unknown metadata field: {key}",
                    doc,
                    field=str(key),
                )
            )

    if "schema_version" not in data:
        issues.append(_issue("M-BASE-E001", "schema_version is missing.", doc, field="schema_version"))
    else:
        sv = data["schema_version"]
        if not isinstance(sv, int) or isinstance(sv, bool) or sv != SCHEMA_VERSION:
            issues.append(
                _issue(
                    "M-BASE-E002",
                    f"schema_version must be integer {SCHEMA_VERSION}, got {sv!r}.",
                    doc,
                    field="schema_version",
                )
            )

    if "id" not in data:
        issues.append(_issue("M-BASE-E012", "id is missing.", doc, field="id"))
    else:
        mid = data["id"]
        if not isinstance(mid, str) or re.fullmatch(ID_PATTERN, mid) is None:
            issues.append(
                _issue(
                    "M-BASE-E010",
                    f"Invalid Method ID: {mid!r}. Expected pattern {ID_PATTERN}.",
                    doc,
                    field="id",
                )
            )
        else:
            doc.object_id = mid
            if mid == RESERVED_METHOD_ID:
                issues.append(
                    _issue(
                        "M-BASE-E011",
                        "Reserved ID M0000 cannot be used for a real Method object.",
                        doc,
                        field="id",
                    )
                )

    if "type" not in data:
        issues.append(_issue("M-BASE-E020", "type is missing.", doc, field="type"))
    elif data["type"] != "method":
        issues.append(
            _issue(
                "M-BASE-E021",
                f"type must be 'method', got {data['type']!r}.",
                doc,
                field="type",
            )
        )

    if "title" not in data:
        issues.append(_issue("M-BASE-E030", "title is missing or empty.", doc, field="title"))
    else:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            issues.append(
                _issue(
                    "M-BASE-E030",
                    "title must be a non-empty string after trim.",
                    doc,
                    field="title",
                )
            )

    if "status" not in data:
        issues.append(_issue("M-STATE-E001", "status is missing.", doc, field="status"))
    else:
        status = data["status"]
        if status not in ALLOWED_STATUSES:
            issues.append(
                _issue(
                    "M-STATE-E001",
                    f"status must be one of {sorted(ALLOWED_STATUSES)}, got {status!r}.",
                    doc,
                    field="status",
                )
            )
        else:
            doc.status = status

    return issues


def validate_unique_ids(documents: list[MethodDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    by_id: dict[str, list[MethodDocument]] = {}
    for doc in documents:
        if doc.object_id:
            by_id.setdefault(doc.object_id, []).append(doc)
    for mid, docs in sorted(by_id.items()):
        if len(docs) < 2:
            continue
        files = [d.relative_path for d in docs]
        for doc in docs:
            issues.append(
                _issue(
                    "M-ID-E001",
                    f"Duplicate Method ID {mid}: {files}",
                    doc,
                    field="id",
                    details={"files": files},
                )
            )
    return issues


def validate_knowledge(
    doc: MethodDocument,
    *,
    knowledge_registry: dict[str, Any] | None,
    knowledge_healthy: bool,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    data = doc.data

    if "knowledge" not in data:
        return issues

    knowledge = data["knowledge"]
    if not isinstance(knowledge, list):
        issues.append(
            _issue(
                "M-KNOW-E001",
                "knowledge must be a YAML list of Knowledge ID strings.",
                doc,
                field="knowledge",
            )
        )
        return issues

    if len(knowledge) == 0:
        issues.append(
            _issue(
                "M-KNOW-E002",
                "knowledge: [] is invalid; omit the field when no formal M→K relation is declared.",
                doc,
                field="knowledge",
            )
        )
        return issues

    seen: set[str] = set()
    for item in knowledge:
        if not isinstance(item, str) or re.fullmatch(KNOWLEDGE_ID_PATTERN, item) is None:
            issues.append(
                _issue(
                    "M-KNOW-E003",
                    f"Invalid Knowledge target ID: {item!r}.",
                    doc,
                    field="knowledge",
                    target_id=str(item) if item is not None else None,
                )
            )
            continue
        if item == RESERVED_KNOWLEDGE_ID:
            issues.append(
                _issue(
                    "M-KNOW-E004",
                    "Knowledge target cannot be reserved ID K0000.",
                    doc,
                    field="knowledge",
                    target_id=item,
                )
            )
            continue
        if item in seen:
            issues.append(
                _issue(
                    "M-KNOW-E005",
                    f"Duplicate Knowledge target: {item}.",
                    doc,
                    field="knowledge",
                    target_id=item,
                )
            )
            continue
        seen.add(item)

        if not knowledge_healthy:
            continue
        if knowledge_registry is None:
            continue
        target = knowledge_registry.get(item)
        if target is None:
            issues.append(
                _issue(
                    "M-KNOW-E006",
                    f"Knowledge target does not exist: {item}.",
                    doc,
                    field="knowledge",
                    target_id=item,
                )
            )
            continue
        target_type = getattr(target, "data", {}).get("type") if hasattr(target, "data") else None
        if target_type is not None and target_type != "knowledge":
            issues.append(
                _issue(
                    "M-KNOW-E007",
                    f"Knowledge target {item} has type {target_type!r}, expected 'knowledge'.",
                    doc,
                    field="knowledge",
                    target_id=item,
                )
            )

    return issues
