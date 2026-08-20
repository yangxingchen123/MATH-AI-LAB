"""Text and JSON reports for Knowledge Workflow."""

from __future__ import annotations

import json
from typing import Any

from .constants import WORKFLOW_VERSION
from .models import WorkflowResult


def format_text(result: WorkflowResult, *, summary_only: bool = False) -> str:
    lines: list[str] = [f"Knowledge Workflow v{WORKFLOW_VERSION}"]
    if summary_only:
        if result.command == "status":
            full = result.stages.get("full_validation")
            index = result.stages.get("index_check")
            lines.append(f"FULL: {full.status if full else 'SKIPPED'}")
            lines.append(f"INDEX: {(index.detail or index.status) if index else 'SKIPPED'}")
        else:
            file_s = result.stages.get("file_validation")
            full = result.stages.get("full_validation")
            index = result.stages.get("index")
            lines.append(f"FILE: {file_s.status if file_s else 'SKIPPED'}")
            lines.append(f"FULL: {full.status if full else 'SKIPPED'}")
            lines.append(f"INDEX: {(index.detail or index.status) if index else 'SKIPPED'}")
        lines.append(result.result)
        return "\n".join(lines) + "\n"

    lines.append("")
    if result.target:
        lines.append("Target:")
        lines.append(result.target)
        lines.append("")

    if result.command == "status":
        full = result.stages["full_validation"]
        index = result.stages["index_check"]
        lines = [
            f"Knowledge Workflow v{WORKFLOW_VERSION}",
            "",
            "[1/2] Full Knowledge validation",
            full.detail or full.status,
        ]
        if full.status == "FAIL":
            for issue in full.issues:
                if issue.severity == "ERROR":
                    lines.append(f"ERROR {issue.rule_id}")
                    lines.append(issue.message)
        lines.append("")
        lines.append("[2/2] Index check")
        lines.append(index.detail or index.status)
        if index.status == "FAIL" or (index.detail in ("STALE", "MISSING")):
            for issue in index.issues:
                lines.append(f"{issue.severity} {issue.rule_id}")
                lines.append(issue.message)
        lines.append("")
        lines.append("Result:")
        lines.append(result.result)
        return "\n".join(lines) + "\n"

    file_s = result.stages["file_validation"]
    full = result.stages["full_validation"]
    index = result.stages["index"]
    lines.append("[1/3] File validation")
    lines.append(file_s.status)
    if file_s.status == "FAIL":
        for issue in file_s.issues:
            if issue.severity in ("ERROR", "WARNING"):
                lines.append(f"{issue.severity} {issue.rule_id}")
                lines.append(issue.message)
    lines.append("")
    lines.append("[2/3] Full Knowledge validation")
    lines.append(full.status)
    if full.status == "FAIL":
        for issue in full.issues:
            if issue.severity == "ERROR":
                lines.append(f"ERROR {issue.rule_id}")
                lines.append(issue.message)
    lines.append("")
    action = "Index sync" if result.command == "sync" else "Index check"
    lines.append(f"[3/3] {action}")
    lines.append(index.detail or index.status)
    if index.status == "FAIL" or (index.detail in ("STALE", "MISSING")):
        for issue in index.issues:
            lines.append(f"{issue.severity} {issue.rule_id}")
            lines.append(issue.message)
    lines.append("")
    lines.append("Result:")
    lines.append(result.result)
    return "\n".join(lines) + "\n"


def format_json(result: WorkflowResult) -> str:
    payload: dict[str, Any] = {
        "workflow_version": WORKFLOW_VERSION,
        "project_root": result.project_root,
        "target": result.target,
        "strict_warnings": result.strict_warnings,
        "stages": {name: stage.to_dict() for name, stage in result.stages.items()},
        "result": result.result,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
