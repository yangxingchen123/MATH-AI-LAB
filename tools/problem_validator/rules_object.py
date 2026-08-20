"""Object-level validation rules for Frozen Problem Schema v1."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from .constants import (
    ALLOWED_STATUSES,
    FROZEN_FIELDS,
    ID_PATTERN,
    KNOWLEDGE_ID_PATTERN,
    RESERVED_KNOWLEDGE_ID,
    RESERVED_PROBLEM_ID,
    SCHEMA_VERSION,
)
from .models import ProblemDocument, Severity, ValidationIssue


def parse_iso_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _issue(
    rule_id: str,
    message: str,
    doc: ProblemDocument,
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


def validate_base(doc: ProblemDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    data = doc.data

    for key in sorted(data.keys(), key=str):
        if key not in FROZEN_FIELDS:
            issues.append(
                _issue(
                    "P-FIELD-W001",
                    f"Unknown metadata field: {key}",
                    doc,
                    field=str(key),
                    severity=Severity.WARNING,
                )
            )

    if "schema_version" not in data:
        issues.append(_issue("P-BASE-E001", "schema_version is missing.", doc, field="schema_version"))
    else:
        sv = data["schema_version"]
        if not isinstance(sv, int) or isinstance(sv, bool) or sv != SCHEMA_VERSION:
            issues.append(
                _issue(
                    "P-BASE-E002",
                    f"schema_version must be integer {SCHEMA_VERSION}, got {sv!r}.",
                    doc,
                    field="schema_version",
                )
            )

    if "id" not in data:
        issues.append(_issue("P-BASE-E012", "id is missing.", doc, field="id"))
    else:
        pid = data["id"]
        if not isinstance(pid, str) or re.fullmatch(ID_PATTERN, pid) is None:
            issues.append(
                _issue(
                    "P-BASE-E010",
                    f"Invalid Problem ID: {pid!r}. Expected pattern {ID_PATTERN}.",
                    doc,
                    field="id",
                )
            )
        else:
            doc.object_id = pid
            if pid == RESERVED_PROBLEM_ID:
                issues.append(
                    _issue(
                        "P-BASE-E011",
                        "Reserved ID P0000 cannot be used for a real Problem object.",
                        doc,
                        field="id",
                    )
                )

    if "type" not in data:
        issues.append(_issue("P-BASE-E020", "type is missing.", doc, field="type"))
    elif data["type"] != "problem":
        issues.append(
            _issue(
                "P-BASE-E021",
                f"type must be 'problem', got {data['type']!r}.",
                doc,
                field="type",
            )
        )

    if "title" not in data:
        issues.append(_issue("P-BASE-E030", "title is missing or empty.", doc, field="title"))
    else:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            issues.append(
                _issue(
                    "P-BASE-E030",
                    "title must be a non-empty string after trim.",
                    doc,
                    field="title",
                )
            )

    if "status" not in data:
        issues.append(_issue("P-STATE-E001", "status is missing.", doc, field="status"))
    else:
        status = data["status"]
        if status not in ALLOWED_STATUSES:
            issues.append(
                _issue(
                    "P-STATE-E001",
                    f"status must be one of {sorted(ALLOWED_STATUSES)}, got {status!r}.",
                    doc,
                    field="status",
                )
            )
        else:
            doc.status = status

    if "created" not in data:
        issues.append(_issue("P-DATE-E001", "created is missing.", doc, field="created"))
    else:
        created = parse_iso_date(data["created"])
        if created is None:
            issues.append(
                _issue(
                    "P-DATE-E001",
                    f"created must be YYYY-MM-DD, got {data['created']!r}.",
                    doc,
                    field="created",
                )
            )
        else:
            doc.created = created

    if "updated" not in data:
        issues.append(_issue("P-DATE-E002", "updated is missing.", doc, field="updated"))
    else:
        updated = parse_iso_date(data["updated"])
        if updated is None:
            issues.append(
                _issue(
                    "P-DATE-E002",
                    f"updated must be YYYY-MM-DD, got {data['updated']!r}.",
                    doc,
                    field="updated",
                )
            )
        else:
            doc.updated = updated

    if doc.created is not None and doc.updated is not None and doc.updated < doc.created:
        issues.append(
            _issue(
                "P-DATE-E003",
                f"updated ({doc.updated.isoformat()}) is earlier than created ({doc.created.isoformat()}).",
                doc,
                field="updated",
            )
        )

    return issues


def validate_unique_ids(documents: list[ProblemDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    by_id: dict[str, list[ProblemDocument]] = {}
    for doc in documents:
        if doc.object_id:
            by_id.setdefault(doc.object_id, []).append(doc)
    for pid, docs in sorted(by_id.items()):
        if len(docs) < 2:
            continue
        files = [d.relative_path for d in docs]
        for doc in docs:
            issues.append(
                _issue(
                    "P-ID-E001",
                    f"Duplicate Problem ID {pid}: {files}",
                    doc,
                    field="id",
                    details={"files": files},
                )
            )
    return issues


def validate_knowledge(
    doc: ProblemDocument,
    *,
    knowledge_registry: dict[str, Any] | None,
    knowledge_healthy: bool,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    data = doc.data
    status = doc.status

    if status == "reviewed" and "knowledge" not in data:
        issues.append(
            _issue(
                "P-KNOW-E002",
                "reviewed Problem must have an explicit knowledge list (empty list is allowed).",
                doc,
                field="knowledge",
            )
        )
        return issues

    if "knowledge" not in data:
        return issues

    knowledge = data["knowledge"]
    if not isinstance(knowledge, list):
        issues.append(
            _issue(
                "P-KNOW-E001",
                "knowledge must be a YAML list of Knowledge ID strings.",
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
                    "P-KNOW-E003",
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
                    "P-KNOW-E004",
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
                    "P-KNOW-E005",
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
                    "P-KNOW-E006",
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
                    "P-KNOW-E007",
                    f"Knowledge target {item} has type {target_type!r}, expected 'knowledge'.",
                    doc,
                    field="knowledge",
                    target_id=item,
                )
            )
            continue
        target_status = getattr(target, "status", None)
        if status == "reviewed" and knowledge and target_status != "reviewed":
            issues.append(
                _issue(
                    "P-KNOW-E008",
                    f"reviewed Problem cannot point to Knowledge {item} with status {target_status!r}.",
                    doc,
                    field="knowledge",
                    target_id=item,
                )
            )
        elif status == "draft" and target_status == "draft":
            issues.append(
                _issue(
                    "P-KNOW-W001",
                    f"draft Problem points to draft Knowledge {item}.",
                    doc,
                    field="knowledge",
                    target_id=item,
                    severity=Severity.WARNING,
                )
            )

    return issues


def validate_parts(doc: ProblemDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if "parts" not in doc.data:
        return issues

    parts = doc.data["parts"]
    if not isinstance(parts, list):
        issues.append(
            _issue(
                "P-PART-E001",
                "parts must be a list of strings.",
                doc,
                field="parts",
            )
        )
        return issues

    tokens: list[str] = []
    for item in parts:
        if not isinstance(item, str):
            issues.append(
                _issue(
                    "P-PART-E001",
                    f"parts tokens must be strings, got {item!r}.",
                    doc,
                    field="parts",
                )
            )
            continue
        token = item.strip()
        if not token:
            issues.append(
                _issue(
                    "P-PART-E002",
                    "parts token is empty after trim.",
                    doc,
                    field="parts",
                )
            )
            continue
        if token in tokens:
            issues.append(
                _issue(
                    "P-PART-E003",
                    f"duplicate parts token: {token!r}.",
                    doc,
                    field="parts",
                )
            )
            continue
        tokens.append(token)

    if not any(i.rule_id in {"P-PART-E001", "P-PART-E002"} for i in issues) and len(tokens) < 2:
        issues.append(
            _issue(
                "P-PART-E004",
                "parts, if present, must contain at least 2 tokens.",
                doc,
                field="parts",
            )
        )
    return issues
