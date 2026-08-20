"""Text report for Workspace Indexer."""

from __future__ import annotations

from .models import IndexOperationResult, IndexResultKind


def format_text(op: IndexOperationResult, *, command: str | None = None) -> str:
    lines = [
        "Workspace Indexer v1.5",
        "",
        f"Project: {op.project_root}",
        f"Index dir: {op.index_dir}/",
        "",
        f"Knowledge validation: {op.knowledge_validator_result}",
        f"Problem validation: {op.problem_validator_result}",
        f"Attempt validation: {op.attempt_validator_result}",
        f"Method validation: {op.method_validator_result}",
        "",
    ]

    if command == "sync":
        if op.result == IndexResultKind.FAIL:
            result_line = "ERROR — source validation failed; no generated files changed"
        elif op.result == IndexResultKind.UP_TO_DATE:
            result_line = "CURRENT — no changes"
        elif op.result == IndexResultKind.BUILT:
            result_line = "UPDATED — generated views synchronized"
        else:
            result_line = op.result.value
        lines.append(f"Result: {result_line}")
    else:
        lines.append(f"Result: {op.result.value}")

    if op.issues:
        lines.append("")
        for issue in op.issues:
            lines.append(f"{issue.severity} [{issue.rule_id}] {issue.message}")
    lines.append("")
    return "\n".join(lines)
