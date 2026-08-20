"""Single-object field rules for Knowledge Schema v1."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from .constants import (
    ALLOWED_STATUSES,
    ID_PATTERN,
    KNOWN_FIELDS,
    RESERVED_ID,
    SCHEMA_VERSION,
)
from .models import KnowledgeDocument, Severity, ValidationIssue


def _issue(
    rule_id: str,
    message: str,
    doc: KnowledgeDocument,
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


def validate_object(doc: KnowledgeDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    data = doc.data

    # Unknown fields
    for key in sorted(data.keys(), key=str):
        if key not in KNOWN_FIELDS:
            issues.append(
                _issue(
                    "K-FIELD-W001",
                    f"Unknown metadata field: {key}",
                    doc,
                    field=str(key),
                    severity=Severity.WARNING,
                )
            )

    # schema_version
    if "schema_version" not in data:
        issues.append(_issue("K-BASE-001", "schema_version is missing.", doc, field="schema_version"))
    else:
        sv = data["schema_version"]
        if not isinstance(sv, int) or isinstance(sv, bool) or sv != SCHEMA_VERSION:
            issues.append(
                _issue(
                    "K-BASE-002",
                    f"schema_version must be integer {SCHEMA_VERSION}, got {sv!r}.",
                    doc,
                    field="schema_version",
                )
            )

    # id
    if "id" not in data:
        issues.append(_issue("K-BASE-012", "id is missing.", doc, field="id"))
    else:
        kid = data["id"]
        if not isinstance(kid, str) or re.fullmatch(ID_PATTERN, kid) is None:
            issues.append(
                _issue(
                    "K-BASE-010",
                    f"Invalid Knowledge ID: {kid!r}. Expected pattern {ID_PATTERN}.",
                    doc,
                    field="id",
                )
            )
        else:
            doc.object_id = kid
            if kid == RESERVED_ID:
                issues.append(
                    _issue(
                        "K-BASE-011",
                        "Reserved ID K0000 cannot be used for a real Knowledge object.",
                        doc,
                        field="id",
                    )
                )

    # type
    if "type" not in data:
        issues.append(_issue("K-BASE-020", "type is missing.", doc, field="type"))
    elif data["type"] != "knowledge":
        issues.append(
            _issue(
                "K-BASE-021",
                f"type must be 'knowledge', got {data['type']!r}.",
                doc,
                field="type",
            )
        )

    # title
    title = data.get("title", None)
    if "title" not in data or not isinstance(title, str) or title.strip() == "":
        issues.append(
            _issue(
                "K-BASE-030",
                "title must be a non-empty string after trim.",
                doc,
                field="title",
            )
        )
    title_str = title.strip() if isinstance(title, str) else None

    # status
    if "status" not in data:
        issues.append(_issue("K-STATE-001", "status is missing.", doc, field="status"))
        status = None
    else:
        status = data["status"]
        if not isinstance(status, str) or status not in ALLOWED_STATUSES:
            issues.append(
                _issue(
                    "K-STATE-001",
                    f"Invalid status: {status!r}. Allowed: draft, reviewed, archived.",
                    doc,
                    field="status",
                )
            )
            status = None
        else:
            doc.status = status

    # dates
    created = None
    updated = None
    if "created" not in data:
        issues.append(_issue("K-DATE-001", "created is missing.", doc, field="created"))
    else:
        created = parse_iso_date(data["created"])
        if created is None:
            issues.append(
                _issue(
                    "K-DATE-001",
                    f"Invalid created date: {data['created']!r}. Expected real YYYY-MM-DD.",
                    doc,
                    field="created",
                )
            )
        else:
            doc.created = created

    if "updated" not in data:
        issues.append(_issue("K-DATE-002", "updated is missing.", doc, field="updated"))
    else:
        updated = parse_iso_date(data["updated"])
        if updated is None:
            issues.append(
                _issue(
                    "K-DATE-002",
                    f"Invalid updated date: {data['updated']!r}. Expected real YYYY-MM-DD.",
                    doc,
                    field="updated",
                )
            )
        else:
            doc.updated = updated

    if created is not None and updated is not None and updated < created:
        issues.append(
            _issue(
                "K-DATE-003",
                f"updated ({updated.isoformat()}) must be >= created ({created.isoformat()}).",
                doc,
                field="updated",
            )
        )

    # aliases
    if "aliases" in data:
        aliases = data["aliases"]
        if not isinstance(aliases, list) or any(not isinstance(a, str) for a in aliases):
            issues.append(
                _issue(
                    "K-FIELD-001",
                    "aliases must be a list of strings.",
                    doc,
                    field="aliases",
                )
            )
        else:
            cleaned: list[str] = []
            seen: set[str] = set()
            for a in aliases:
                item = a.strip()
                if item == "":
                    issues.append(
                        _issue(
                            "K-FIELD-001",
                            "aliases entries must be non-empty after trim.",
                            doc,
                            field="aliases",
                        )
                    )
                    continue
                if title_str is not None and item == title_str:
                    issues.append(
                        _issue(
                            "K-FIELD-002",
                            "alias must not duplicate title.",
                            doc,
                            field="aliases",
                        )
                    )
                if item in seen:
                    issues.append(
                        _issue(
                            "K-FIELD-003",
                            f"duplicate alias after trim: {item!r}.",
                            doc,
                            field="aliases",
                        )
                    )
                else:
                    seen.add(item)
                    cleaned.append(item)
            doc.aliases = cleaned
    elif status == "reviewed":
        issues.append(
            _issue(
                "K-FIELD-007",
                "reviewed Knowledge requires aliases (use [] if none).",
                doc,
                field="aliases",
            )
        )

    # domain
    if "domain" in data:
        domain = data["domain"]
        if not isinstance(domain, str) or domain.strip() == "":
            issues.append(
                _issue(
                    "K-FIELD-004",
                    "domain must be a non-empty string after trim.",
                    doc,
                    field="domain",
                )
            )
        else:
            doc.domain = domain.strip()
    elif status == "reviewed":
        issues.append(
            _issue(
                "K-FIELD-008",
                "reviewed Knowledge requires non-empty domain.",
                doc,
                field="domain",
            )
        )

    # prerequisites
    if "prerequisites" in data:
        prereqs = data["prerequisites"]
        if not isinstance(prereqs, list):
            issues.append(
                _issue(
                    "K-FIELD-005",
                    "prerequisites must be a list.",
                    doc,
                    field="prerequisites",
                )
            )
        else:
            doc.prerequisites = []
            for item in prereqs:
                if not isinstance(item, str):
                    issues.append(
                        _issue(
                            "K-FIELD-005",
                            f"prerequisites entries must be strings, got {item!r}.",
                            doc,
                            field="prerequisites",
                        )
                    )
                else:
                    doc.prerequisites.append(item)
    elif status == "reviewed":
        issues.append(
            _issue(
                "K-FIELD-009",
                "reviewed Knowledge requires prerequisites (use [] if none).",
                doc,
                field="prerequisites",
            )
        )

    # related
    if "related" in data:
        related = data["related"]
        if not isinstance(related, list):
            issues.append(
                _issue(
                    "K-FIELD-006",
                    "related must be a list.",
                    doc,
                    field="related",
                )
            )
        else:
            doc.related = []
            for item in related:
                if not isinstance(item, str):
                    issues.append(
                        _issue(
                            "K-FIELD-006",
                            f"related entries must be strings, got {item!r}.",
                            doc,
                            field="related",
                        )
                    )
                else:
                    doc.related.append(item)
    elif status == "reviewed":
        issues.append(
            _issue(
                "K-FIELD-010",
                "reviewed Knowledge requires related (use [] if none).",
                doc,
                field="related",
            )
        )

    return issues
