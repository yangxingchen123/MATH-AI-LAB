"""Cross-object relation rules for Knowledge Schema v1."""

from __future__ import annotations

import re
from typing import Mapping

from .constants import ID_PATTERN, RESERVED_ID
from .models import KnowledgeDocument, Severity, ValidationIssue


def _issue(
    rule_id: str,
    message: str,
    doc: KnowledgeDocument,
    *,
    field: str,
    target_id: str | None = None,
    severity: Severity = Severity.ERROR,
) -> ValidationIssue:
    return ValidationIssue(
        severity=severity,
        rule_id=rule_id,
        message=message,
        file=doc.relative_path,
        object_id=doc.object_id,
        field=field,
        target_id=target_id,
    )


def _validate_id_list(
    doc: KnowledgeDocument,
    field: str,
    values: list[str] | None,
    registry: Mapping[str, KnowledgeDocument],
) -> list[ValidationIssue]:
    if values is None:
        return []

    issues: list[ValidationIssue] = []
    seen: set[str] = set()

    for target in values:
        if re.fullmatch(ID_PATTERN, target) is None:
            issues.append(
                _issue(
                    "K-REL-007",
                    f"Invalid {field} target ID format: {target!r}.",
                    doc,
                    field=field,
                    target_id=target,
                )
            )
            continue

        if target == RESERVED_ID:
            issues.append(
                _issue(
                    "K-REL-006",
                    f"{field} must not reference reserved ID K0000.",
                    doc,
                    field=field,
                    target_id=target,
                )
            )
            continue

        if doc.object_id is not None and target == doc.object_id:
            issues.append(
                _issue(
                    "K-REL-002",
                    f"{field} must not self-reference {target}.",
                    doc,
                    field=field,
                    target_id=target,
                )
            )
            continue

        if target in seen:
            issues.append(
                _issue(
                    "K-REL-003",
                    f"Duplicate {field} reference: {target}.",
                    doc,
                    field=field,
                    target_id=target,
                )
            )
            continue
        seen.add(target)

        target_doc = registry.get(target)
        if target_doc is None:
            issues.append(
                _issue(
                    "K-REL-001",
                    f"Referenced Knowledge {target} does not exist.",
                    doc,
                    field=field,
                    target_id=target,
                )
            )
            continue

        # Target type: registry only contains knowledge candidates, but verify.
        if target_doc.data.get("type") != "knowledge":
            issues.append(
                _issue(
                    "K-REL-001",
                    f"Relation target {target} is not type knowledge.",
                    doc,
                    field=field,
                    target_id=target,
                )
            )
            continue

        source_status = doc.status
        target_status = target_doc.status

        if source_status == "reviewed":
            if target_status != "reviewed":
                issues.append(
                    _issue(
                        "K-REL-005",
                        f"reviewed source requires reviewed target; {target} has status {target_status!r}.",
                        doc,
                        field=field,
                        target_id=target,
                    )
                )
        elif source_status == "draft":
            if target_status == "draft":
                issues.append(
                    _issue(
                        "K-REL-W001",
                        f"draft source references draft target {target}.",
                        doc,
                        field=field,
                        target_id=target,
                        severity=Severity.WARNING,
                    )
                )
            elif target_status == "archived":
                issues.append(
                    _issue(
                        "K-REL-W002",
                        f"draft source references archived target {target} "
                        "(Knowledge Schema v1 does not explicitly allow this; SCHEMA_AMBIGUITY).",
                        doc,
                        field=field,
                        target_id=target,
                        severity=Severity.WARNING,
                    )
                )
        # archived source: historical refs parseable; existence already checked.

    return issues


def validate_relations(
    doc: KnowledgeDocument,
    registry: Mapping[str, KnowledgeDocument],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(_validate_id_list(doc, "prerequisites", doc.prerequisites, registry))
    issues.extend(_validate_id_list(doc, "related", doc.related, registry))

    if doc.prerequisites is not None and doc.related is not None:
        prereq_set = set(doc.prerequisites)
        overlap = sorted(prereq_set.intersection(doc.related))
        for target in overlap:
            # Only report well-formed IDs that aren't reserved/self already flagged
            if re.fullmatch(ID_PATTERN, target) and target != RESERVED_ID:
                issues.append(
                    _issue(
                        "K-REL-004",
                        f"Knowledge ID {target} appears in both prerequisites and related.",
                        doc,
                        field="related",
                        target_id=target,
                    )
                )
    return issues


def validate_unique_ids(documents: list[KnowledgeDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    first_seen: dict[str, KnowledgeDocument] = {}
    for doc in documents:
        kid = doc.object_id
        if kid is None:
            continue
        if kid in first_seen:
            first = first_seen[kid]
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="K-BASE-040",
                    message=f"Duplicate Knowledge ID {kid}.",
                    file=doc.relative_path,
                    object_id=kid,
                    field="id",
                    details={
                        "duplicate_id": kid,
                        "first_path": first.relative_path,
                        "second_path": doc.relative_path,
                    },
                )
            )
            # Also annotate the first file once if not already reported for this pair
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    rule_id="K-BASE-040",
                    message=f"Duplicate Knowledge ID {kid}.",
                    file=first.relative_path,
                    object_id=kid,
                    field="id",
                    details={
                        "duplicate_id": kid,
                        "first_path": first.relative_path,
                        "second_path": doc.relative_path,
                    },
                )
            )
        else:
            first_seen[kid] = doc
    # Deduplicate identical issues from multiple duplicates of same id
    unique: list[ValidationIssue] = []
    seen_keys: set[tuple] = set()
    for issue in issues:
        key = (issue.file, issue.object_id, issue.rule_id, tuple(sorted(issue.details.items())))
        if key not in seen_keys:
            seen_keys.add(key)
            unique.append(issue)
    return unique
