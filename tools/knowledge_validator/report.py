"""Text and JSON reporting for validation results."""

from __future__ import annotations

import json
from typing import Any

from .constants import SCHEMA_OBJECT_TYPE, SCHEMA_STATUS, SCHEMA_VERSION, VALIDATOR_VERSION
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


def result_to_dict(result: ValidationResult) -> dict[str, Any]:
    return {
        "validator_version": VALIDATOR_VERSION,
        "schema": {
            "object_type": SCHEMA_OBJECT_TYPE,
            "schema_version": SCHEMA_VERSION,
            "status": SCHEMA_STATUS,
        },
        "project_root": str(result.project_root),
        "summary": {
            "markdown_files": result.summary.markdown_files,
            "knowledge_objects": result.summary.knowledge_objects,
            "excluded_files": result.summary.excluded_files,
            "skipped_files": result.summary.skipped_files,
            "errors": result.summary.errors,
            "warnings": result.summary.warnings,
            "info": result.summary.info,
            "result": result.summary.result,
        },
        "issues": [issue_to_dict(i) for i in result.issues],
    }


def format_json(result: ValidationResult) -> str:
    return json.dumps(result_to_dict(result), ensure_ascii=False, indent=2)


def format_text(result: ValidationResult, *, summary_only: bool = False, verbose: bool = False) -> str:
    lines: list[str] = []
    lines.append(f"Knowledge Validator v{VALIDATOR_VERSION}")
    lines.append(f"Schema: Knowledge v{SCHEMA_VERSION} ({SCHEMA_STATUS.capitalize()})")
    lines.append("")
    lines.append("Project:")
    lines.append(str(result.project_root))
    lines.append("")

    if summary_only:
        lines.append(f"Knowledge objects: {result.summary.knowledge_objects}")
        lines.append(f"Errors: {result.summary.errors}")
        lines.append(f"Warnings: {result.summary.warnings}")
        lines.append(result.summary.result)
        return "\n".join(lines) + "\n"

    lines.append(f"Scanned Markdown: {result.summary.markdown_files}")
    lines.append(f"Knowledge objects: {result.summary.knowledge_objects}")
    lines.append(f"Excluded templates: {result.summary.excluded_files}")
    if result.summary.skipped_files:
        lines.append(f"Skipped (no metadata): {result.summary.skipped_files}")
    lines.append("")
    lines.append(f"Errors: {result.summary.errors}")
    lines.append(f"Warnings: {result.summary.warnings}")
    lines.append(f"Info: {result.summary.info}")
    lines.append("")

    if verbose:
        lines.append("Documents:")
        for doc in result.documents:
            oid = doc.object_id or "?"
            lines.append(f"  - {oid}: {doc.relative_path}")
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
