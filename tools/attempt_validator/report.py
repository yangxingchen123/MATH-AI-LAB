"""Text and JSON reporting for Attempt Validator v1."""

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
        "problem": doc.problem,
        "part": doc.part,
        "outcome": doc.outcome,
    }


def result_to_dict(result: ValidationResult) -> dict[str, Any]:
    return {
        "validator": f"attempt_validator v{VALIDATOR_VERSION}",
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
            "attempt_objects": result.summary.attempt_objects,
            "errors": result.summary.errors,
            "warnings": result.summary.warnings,
            "info": result.summary.info,
            "result": result.summary.result,
        },
        "dependency": {
            "healthy": result.dependency.healthy,
            "errors": result.dependency.errors,
            "warnings": result.dependency.warnings,
            "problem_objects": result.dependency.problem_objects,
            "result": result.dependency.result,
        },
        "issues": [issue_to_dict(i) for i in result.issues],
        "documents": [document_summary(d) for d in result.documents],
        "registry_ids": sorted(result.registry.keys()),
        "result": result.summary.result,
    }


def format_json(result: ValidationResult) -> str:
    return json.dumps(result_to_dict(result), ensure_ascii=False, indent=2)


def format_text(result: ValidationResult, *, summary_only: bool = False, verbose: bool = False) -> str:
    lines: list[str] = []
    lines.append(f"Attempt Validator v{VALIDATOR_VERSION}")
    lines.append(
        f"Schema: Attempt v{SCHEMA_VERSION} ({SCHEMA_STATUS.capitalize()}, {SCHEMA_FROZEN_DATE})"
    )
    lines.append("")
    lines.append("Project:")
    lines.append(str(result.project_root))
    lines.append("")

    if result.focus_relative_path:
        lines.append(f"Focus: {result.focus_relative_path}")
        lines.append("")

    lines.append(f"Scanned Markdown: {result.summary.markdown_files}")
    lines.append(f"Attempt objects: {result.summary.attempt_objects}")
    lines.append("")
    lines.append("Problem dependency:")
    lines.append(f"  {result.dependency.result} ({result.dependency.problem_objects} Problem objects)")
    lines.append("")

    lines.append(f"Errors: {result.summary.errors}")
    lines.append(f"Warnings: {result.summary.warnings}")
    if verbose:
        lines.append(f"Info: {result.summary.info}")
    lines.append("")

    if summary_only:
        lines.append(result.summary.result)
        return "\n".join(lines) + "\n"

    if result.issues:
        for issue in result.issues:
            if issue.severity == Severity.INFO and not verbose:
                continue
            loc = issue.file or "-"
            oid = issue.object_id or "-"
            field = issue.field or "-"
            lines.append(
                f"[{issue.severity.value}] {issue.rule_id} | {loc} | {oid} | {field} | {issue.message}"
            )
        lines.append("")

    if verbose and result.documents:
        lines.append("Documents:")
        for doc in result.documents:
            lines.append(f"  {doc.object_id} @ {doc.relative_path}")
        lines.append("")

    lines.append(result.summary.result)
    return "\n".join(lines) + "\n"
