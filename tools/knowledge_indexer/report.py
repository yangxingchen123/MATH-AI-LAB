"""CLI text/JSON reporting for Knowledge Indexer."""

from __future__ import annotations

import json
from typing import Any

from tools.knowledge_validator.constants import VALIDATOR_VERSION
from tools.knowledge_validator.report import issue_to_dict

from .constants import INDEXER_VERSION
from .models import IndexOperationResult


def format_text(op: IndexOperationResult, *, summary_only: bool = False) -> str:
    lines: list[str] = []
    lines.append(f"Knowledge Indexer v{INDEXER_VERSION}")
    lines.append("Schema: Knowledge v1 (Frozen)")
    lines.append(f"Validator: Knowledge Validator v{VALIDATOR_VERSION}")
    lines.append("")
    if summary_only:
        lines.append(f"Knowledge objects: {op.knowledge_objects}")
        lines.append(f"Result: {op.result.value}")
        return "\n".join(lines) + "\n"

    lines.append(f"Project: {op.project_root}")
    lines.append(f"Index: {op.index_dir}")
    lines.append("")
    lines.append(f"Validator: {op.validator_result} (errors={op.validator_errors}, warnings={op.validator_warnings})")
    lines.append(f"Knowledge objects: {op.knowledge_objects}")
    lines.append(f"Domains: {op.domains}")
    lines.append(f"Prerequisite edges: {op.prerequisite_edges}")
    lines.append(f"Related declared edges: {op.related_declared_edges}")
    lines.append(f"Related effective edges: {op.related_effective_edges}")
    lines.append("")
    if op.validator_issues and op.validator_errors:
        lines.append("Validator issues:")
        for issue in op.validator_issues:
            if issue.severity.value == "ERROR":
                lines.append(f"  ERROR {issue.rule_id}: {issue.message}")
        lines.append("")
    if op.issues:
        lines.append("Indexer issues:")
        for issue in op.issues:
            lines.append(f"  {issue.severity} {issue.rule_id}: {issue.message}")
        lines.append("")
    lines.append(f"Result: {op.result.value}")
    return "\n".join(lines) + "\n"


def format_json(op: IndexOperationResult) -> str:
    payload: dict[str, Any] = {
        "indexer_version": INDEXER_VERSION,
        "schema_version": 1,
        "validator": {
            "version": VALIDATOR_VERSION,
            "errors": op.validator_errors,
            "warnings": op.validator_warnings,
            "result": op.validator_result,
            "issues": [issue_to_dict(i) for i in op.validator_issues],
        },
        "project_root": op.project_root,
        "index_dir": op.index_dir,
        "summary": {
            "knowledge_objects": op.knowledge_objects,
            "domains": op.domains,
            "prerequisite_edges": op.prerequisite_edges,
            "related_declared_edges": op.related_declared_edges,
            "related_effective_edges": op.related_effective_edges,
        },
        "result": op.result.value,
        "issues": [
            {
                "severity": i.severity,
                "rule_id": i.rule_id,
                "message": i.message,
                "details": i.details,
            }
            for i in op.issues
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
