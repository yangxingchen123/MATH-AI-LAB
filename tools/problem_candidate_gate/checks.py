"""Mechanical Candidate checks (v0.1; not Frozen Schema contract)."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .constants import (
    ALLOWED_STATUSES,
    CONTENT_REVIEW_MARKER,
    ID_PATTERN,
    KNOWLEDGE_ID_PATTERN,
    KNOWN_FIELDS,
    RESERVED_KNOWLEDGE_ID,
    RESERVED_PROBLEM_ID,
    SCHEMA_VERSION,
)
from .models import GateIssue, ProblemDocument, Severity


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
) -> GateIssue:
    return GateIssue(
        severity=severity,
        rule_id=rule_id,
        message=message,
        file=doc.relative_path,
        object_id=doc.object_id,
        field=field,
        target_id=target_id,
        details=details or {},
    )


def validate_base(doc: ProblemDocument) -> list[GateIssue]:
    issues: list[GateIssue] = []
    data = doc.data

    for key in sorted(data.keys(), key=str):
        if key not in KNOWN_FIELDS:
            issues.append(
                _issue(
                    "PCG-FIELD-W001",
                    f"Unknown metadata field: {key}",
                    doc,
                    field=str(key),
                    severity=Severity.WARNING,
                )
            )

    if "schema_version" not in data:
        issues.append(_issue("PCG-BASE-001", "schema_version is missing.", doc, field="schema_version"))
    else:
        sv = data["schema_version"]
        if not isinstance(sv, int) or isinstance(sv, bool) or sv != SCHEMA_VERSION:
            issues.append(
                _issue(
                    "PCG-BASE-002",
                    f"schema_version must be integer {SCHEMA_VERSION}, got {sv!r}.",
                    doc,
                    field="schema_version",
                )
            )

    if "id" not in data:
        issues.append(_issue("PCG-BASE-012", "id is missing.", doc, field="id"))
    else:
        pid = data["id"]
        if not isinstance(pid, str) or re.fullmatch(ID_PATTERN, pid) is None:
            issues.append(
                _issue(
                    "PCG-BASE-010",
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
                        "PCG-BASE-011",
                        "Reserved ID P0000 cannot be used for a real Problem object.",
                        doc,
                        field="id",
                    )
                )

    if "type" not in data:
        issues.append(_issue("PCG-BASE-020", "type is missing.", doc, field="type"))
    elif data["type"] != "problem":
        issues.append(
            _issue(
                "PCG-BASE-021",
                f"type must be 'problem', got {data['type']!r}.",
                doc,
                field="type",
            )
        )

    if "title" not in data:
        issues.append(_issue("PCG-BASE-030", "title is missing or empty.", doc, field="title"))
    else:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            issues.append(
                _issue(
                    "PCG-BASE-030",
                    "title must be a non-empty string after trim.",
                    doc,
                    field="title",
                )
            )

    if "status" not in data:
        issues.append(_issue("PCG-STATE-001", "status is missing.", doc, field="status"))
    else:
        status = data["status"]
        if status not in ALLOWED_STATUSES:
            issues.append(
                _issue(
                    "PCG-STATE-001",
                    f"status must be one of {sorted(ALLOWED_STATUSES)}, got {status!r}.",
                    doc,
                    field="status",
                )
            )
        else:
            doc.status = status

    if "created" not in data:
        issues.append(_issue("PCG-DATE-001", "created is missing.", doc, field="created"))
    else:
        created = parse_iso_date(data["created"])
        if created is None:
            issues.append(
                _issue(
                    "PCG-DATE-001",
                    f"created must be YYYY-MM-DD, got {data['created']!r}.",
                    doc,
                    field="created",
                )
            )
        else:
            doc.created = created

    if "updated" not in data:
        issues.append(_issue("PCG-DATE-002", "updated is missing.", doc, field="updated"))
    else:
        updated = parse_iso_date(data["updated"])
        if updated is None:
            issues.append(
                _issue(
                    "PCG-DATE-002",
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
                "PCG-DATE-003",
                f"updated ({doc.updated.isoformat()}) is earlier than created ({doc.created.isoformat()}).",
                doc,
                field="updated",
            )
        )

    return issues


def validate_unique_ids(documents: list[ProblemDocument]) -> list[GateIssue]:
    issues: list[GateIssue] = []
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
                    "PCG-ID-001",
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
) -> list[GateIssue]:
    issues: list[GateIssue] = []
    data = doc.data
    status = doc.status

    if status == "reviewed" and "knowledge" not in data:
        issues.append(
            _issue(
                "PCG-KNOW-002",
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
                "PCG-KNOW-001",
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
                    "PCG-KNOW-003",
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
                    "PCG-KNOW-004",
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
                    "PCG-KNOW-005",
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
                    "PCG-KNOW-006",
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
                    "PCG-KNOW-007",
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
                    "PCG-KNOW-008",
                    f"reviewed Problem cannot point to Knowledge {item} with status {target_status!r}.",
                    doc,
                    field="knowledge",
                    target_id=item,
                )
            )
        elif status == "draft" and target_status == "draft":
            issues.append(
                _issue(
                    "PCG-KNOW-W001",
                    f"draft Problem points to draft Knowledge {item} (Candidate warning).",
                    doc,
                    field="knowledge",
                    target_id=item,
                    severity=Severity.WARNING,
                )
            )

    return issues


SIMPLE_PART_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def validate_parts(doc: ProblemDocument) -> list[GateIssue]:
    issues: list[GateIssue] = []
    if "parts" not in doc.data:
        return issues

    parts = doc.data["parts"]
    if not isinstance(parts, list):
        issues.append(
            _issue(
                "PCG-PART-001",
                "parts must be a list of strings (Candidate v0.1 provisional).",
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
                    "PCG-PART-001",
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
                    "PCG-PART-002",
                    "parts token is empty after trim.",
                    doc,
                    field="parts",
                )
            )
            continue
        if token in tokens:
            issues.append(
                _issue(
                    "PCG-PART-003",
                    f"duplicate parts token: {token!r}.",
                    doc,
                    field="parts",
                )
            )
            continue
        tokens.append(token)
        if (
            item != token
            or "\n" in item
            or " " in item
            or len(token) > 32
            or SIMPLE_PART_RE.fullmatch(token) is None
        ):
            issues.append(
                _issue(
                    "PCG-PART-W001",
                    f"complex parts token {item!r}; prefer simple stable ASCII anchors.",
                    doc,
                    field="parts",
                    severity=Severity.WARNING,
                )
            )

    if not any(i.rule_id in {"PCG-PART-001", "PCG-PART-002"} for i in issues) and len(tokens) < 2:
        issues.append(
            _issue(
                "PCG-PART-004",
                "parts, if present, must contain at least 2 tokens (Candidate v0.1 provisional).",
                doc,
                field="parts",
            )
        )
    return issues


def validate_legacy_filename(doc: ProblemDocument) -> list[GateIssue]:
    if not doc.object_id:
        return []
    stem = Path(doc.path).stem
    match = re.match(r"^(P\d+)", stem)
    if not match:
        return []
    file_id = match.group(1)
    if file_id != doc.object_id:
        return [
            _issue(
                "PCG-LEGACY-W001",
                "Legacy filename ID does not match canonical Pdddd ID.",
                doc,
                field="id",
                severity=Severity.WARNING,
                details={"filename_id": file_id, "canonical_id": doc.object_id},
            )
        ]
    return []


def validate_content_review_marker(doc: ProblemDocument) -> list[GateIssue]:
    if CONTENT_REVIEW_MARKER in doc.body:
        return [
            _issue(
                "PCG-READY-W001",
                "Candidate Content Review pending (exact Markdown marker).",
                doc,
                severity=Severity.WARNING,
            )
        ]
    return []


def validate_directory_info(doc: ProblemDocument, *, verbose: bool) -> list[GateIssue]:
    if not verbose:
        return []
    return [
        _issue(
            "PCG-DISC-I001",
            "Directory workflow state (未解决/研究中/已解决) is non-authoritative for Problem Object Status.",
            doc,
            severity=Severity.INFO,
        )
    ]
