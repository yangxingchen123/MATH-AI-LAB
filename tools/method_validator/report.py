"""Text and JSON reporting for Method Validator v1."""

from __future__ import annotations

import json
from typing import Any

from .constants import SCHEMA_FROZEN_DATE, SCHEMA_OBJECT_TYPE, SCHEMA_STATUS, SCHEMA_VERSION, VALIDATOR_VERSION
from .models import Severity, ValidationIssue, ValidationResult


def issue_to_dict(issue: ValidationIssue) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "severity": issue.severity.value,
        "rule_id": issue.rule_id,
        "message": issue.message,
        "file": issue.file,
        "object_id": issue.object_id,
        "field": issue.field,
        "target_id": issue.target_id,
    }
    if issue.details:
        payload["details"] = issue.details
    return payload


def document_summary(doc) -> dict[str, Any]:
    return {
        "id": doc.object_id,
        "path": doc.relative_path,
        "status": doc.status,
    }


def result_to_dict(result: ValidationResult) -> dict[str, Any]:
    return {
        "validator": f"method_validator v{VALIDATOR_VERSION}",
        "schema_version": SCHEMA_VERSION,
        "schema": {
            "object_type": SCHEMA_OBJECT_TYPE,
            "schema_version": SCHEMA_VERSION,
            "status": SCHEMA_STATUS,
            "frozen_date": SCHEMA_FROZEN_DATE,
        },
        "project_root": str(result.project_root),
        "summary": {
            "markdown_files": result.summary.markdown_files,
            "method_objects": result.summary.method_objects,
            "errors": result.summary.errors,
            "warnings": result.summary.warnings,
            "info": result.summary.info,
            "result": result.summary.result,
        },
        "dependency": {
            "healthy": result.dependency.healthy,
            "errors": result.dependency.errors,
            "warnings": result.dependency.warnings,
            "knowledge_objects": result.dependency.knowledge_objects,
            "result": result.dependency.result,
        },
        "registry_available": result.registry_available,
        "registry_ids": sorted(result.registry.keys()),
        "issues": [issue_to_dict(i) for i in result.issues],
        "documents": [document_summary(d) for d in result.documents],
        "result": result.summary.result,
    }


def format_json(result: ValidationResult) -> str:
    return json.dumps(result_to_dict(result), ensure_ascii=False, indent=2)


def format_text(result: ValidationResult, *, summary_only: bool = False, verbose: bool = False) -> str:
    lines: list[str] = []
    lines.append(f"Method Validator v{VALIDATOR_VERSION}")
    lines.append(f"Schema: Method v{SCHEMA_VERSION} ({SCHEMA_STATUS.capitalize()}, {SCHEMA_FROZEN_DATE})")
    lines.append("")
    lines.append("Project:")
    lines.append(str(result.project_root))
    lines.append("")

    if summary_only:
        lines.append(f"Method objects: {result.summary.method_objects}")
        lines.append(f"Errors: {result.summary.errors}")
        lines.append(f"Warnings: {result.summary.warnings}")
        if not result.dependency.healthy:
            lines.append("Knowledge dependency: FAILED")
        if result.registry_available:
            lines.append(f"Validated registry: AVAILABLE ({len(result.registry)} objects)")
        else:
            lines.append("Validated registry: NOT AVAILABLE")
        lines.append(result.summary.result)
        return "\n".join(lines) + "\n"

    lines.append(f"Scanned Markdown: {result.summary.markdown_files}")
    lines.append(f"Method objects: {result.summary.method_objects}")
    lines.append("")
    lines.append("Knowledge dependency:")
    if result.dependency.healthy:
        lines.append(f"  PASS ({result.dependency.knowledge_objects} Knowledge objects)")
    else:
        lines.append(f"  FAILED ({result.dependency.errors} Knowledge errors)")
    lines.append("")
    if result.registry_available:
        lines.append(f"Validated registry: AVAILABLE ({len(result.registry)} objects)")
    else:
        lines.append("Validated registry: NOT AVAILABLE")
    lines.append("")
    lines.append(f"Errors: {result.summary.errors}")
    lines.append(f"Warnings: {result.summary.warnings}")
    lines.append(f"Info: {result.summary.info}")
    lines.append("")

    if verbose:
        lines.append("Documents:")
        for doc in result.documents:
            oid = doc.object_id or "?"
            lines.append(f"  - {oid}: {doc.relative_path} (status={doc.status})")
        if result.registry:
            lines.append("")
            lines.append("Registry IDs:")
            for mid in sorted(result.registry.keys()):
                lines.append(f"  - {mid}")
        lines.append("")

    visible = result.issues
    if not verbose:
        visible = [i for i in result.issues if i.severity != Severity.INFO]

    for issue in visible:
        lines.append(f"{issue.severity.value} {issue.rule_id}")
        if issue.object_id:
            lines.append(f"Object: {issue.object_id}")
        if issue.file:
            lines.append(f"File: {issue.file}")
        if issue.field:
            lines.append(f"Field: {issue.field}")
        if issue.target_id:
            lines.append(f"Target: {issue.target_id}")
        lines.append(f"Message: {issue.message}")
        if issue.details:
            for k in sorted(issue.details.keys()):
                lines.append(f"{k}: {issue.details[k]}")
        lines.append("")

    lines.append(result.summary.result)
    return "\n".join(lines) + "\n"
