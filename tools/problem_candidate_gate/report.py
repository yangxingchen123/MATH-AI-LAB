"""Text and JSON reporting for Problem Candidate Gate v0.1."""

from __future__ import annotations

import json
from typing import Any

from .constants import GATE_VERSION, MANUAL_REVIEW_ITEMS, SCHEMA_OBJECT_TYPE, SCHEMA_STATUS, SCHEMA_VERSION
from .models import GateIssue, GateResult, Severity


def issue_to_dict(issue: GateIssue) -> dict[str, Any]:
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


def result_to_dict(result: GateResult, *, include_readiness: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "gate_version": GATE_VERSION,
        "candidate_schema": {
            "object_type": SCHEMA_OBJECT_TYPE,
            "schema_version": SCHEMA_VERSION,
            "status": SCHEMA_STATUS,
        },
        "project_root": str(result.project_root),
        "summary": {
            "problem_candidates": result.summary.problem_candidates,
            "markdown_files": result.summary.markdown_files,
            "excluded_files": result.summary.excluded_files,
            "skipped_files": result.summary.skipped_files,
            "errors": result.summary.errors,
            "warnings": result.summary.warnings,
            "info": result.summary.info,
        },
        "automated_gates": {
            "result": "PASS" if result.summary.errors == 0 else "FAIL",
            "knowledge_dependency_ok": result.knowledge_dependency_ok,
        },
        "issues": [issue_to_dict(i) for i in result.issues],
    }
    if include_readiness:
        payload["manual_review_items"] = result.manual_review_items or list(MANUAL_REVIEW_ITEMS)
        payload["result"] = result.readiness or result.summary.result
        payload["summary"]["result"] = result.readiness
    else:
        payload["summary"]["result"] = result.summary.result
        payload["result"] = result.summary.result
    return payload


def format_json(result: GateResult, *, include_readiness: bool = False) -> str:
    return json.dumps(result_to_dict(result, include_readiness=include_readiness), ensure_ascii=False, indent=2)


def format_text(
    result: GateResult,
    *,
    summary_only: bool = False,
    verbose: bool = False,
    include_readiness: bool = False,
) -> str:
    lines: list[str] = []
    lines.append(f"Problem Candidate Gate v{GATE_VERSION}")
    lines.append("Temporary pre-freeze quality gate for Problem Schema v1 Candidate.")
    lines.append("Not the formal Problem Validator v1.")
    lines.append("")
    lines.append("Project:")
    lines.append(str(result.project_root))
    lines.append("")

    if summary_only:
        lines.append(f"Problem candidates: {result.summary.problem_candidates}")
        lines.append(f"Errors: {result.summary.errors}")
        lines.append(f"Warnings: {result.summary.warnings}")
        if include_readiness:
            lines.append(f"Automated Gates: {'PASS' if result.summary.errors == 0 else 'FAIL'}")
            lines.append(result.readiness or result.summary.result)
        else:
            lines.append(result.summary.result)
        return "\n".join(lines) + "\n"

    lines.append(f"Scanned Markdown: {result.summary.markdown_files}")
    lines.append(f"Problem candidates: {result.summary.problem_candidates}")
    lines.append(f"Excluded templates: {result.summary.excluded_files}")
    if result.summary.skipped_files:
        lines.append(f"Skipped (no metadata): {result.summary.skipped_files}")
    lines.append("")
    lines.append("Automated Gates:")
    lines.append("PASS" if result.summary.errors == 0 else "FAIL")
    lines.append("")
    lines.append(f"Errors: {result.summary.errors}")
    lines.append(f"Warnings: {result.summary.warnings}")
    lines.append(f"Info: {result.summary.info}")
    lines.append("")

    visible = result.issues
    if not verbose:
        visible = [i for i in result.issues if i.severity != Severity.INFO]

    if visible:
        lines.append("Issues:")
        for issue in visible:
            loc = issue.file or ""
            oid = f" [{issue.object_id}]" if issue.object_id else ""
            lines.append(f"- {issue.severity.value} {issue.rule_id}{oid} {loc}: {issue.message}")
        lines.append("")

    if include_readiness:
        lines.append("Manual Review:")
        for item in result.manual_review_items or MANUAL_REVIEW_ITEMS:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("Result:")
        lines.append(result.readiness or "NOT_READY")
        lines.append("")
    else:
        lines.append(result.summary.result)
        lines.append("")

    return "\n".join(lines)
