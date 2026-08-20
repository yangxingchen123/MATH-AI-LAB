"""Text report for Workspace Check."""

from __future__ import annotations

from .checker import WorkspaceCheckResult


def format_text(result: WorkspaceCheckResult) -> str:
    lines = [
        "MATH-AI-LAB Workspace Check",
        "",
        f"Knowledge validation: {result.knowledge_validation}",
        f"Problem validation: {result.problem_validation}",
        f"Attempt validation: {result.attempt_validation}",
        f"Method validation: {result.method_validation}",
        "",
        "Repository facts",
        "----------------",
    ]
    facts = result.repository_facts
    if facts:
        lines.append(f"Knowledge entries: {facts.get('knowledge_entries', 0)}")
        lines.append(f"Problems: {facts.get('problems', 0)}")
        if "attempts" in facts:
            lines.append(f"Attempts: {facts.get('attempts', 0)}")
        if "methods" in facts:
            lines.append(f"Methods: {facts.get('methods', 0)}")
        wf = facts.get("workflow_counts") or {}
        for name in sorted(wf):
            lines.append(f"  {name}: {wf[name]}")
        lines.append(f"Published PDF files: {facts.get('published_pdfs', 0)}")
        lines.append(f"LaTeX projects: {facts.get('latex_projects', 0)}")
    else:
        lines.append("(skipped — validation errors)")

    if result.generated_status:
        lines.extend(["", "Generated views", "---------------"])
        for name in sorted(result.generated_status):
            lines.append(f"{name}: {result.generated_status[name]}")

    if result.issues:
        lines.append("")
        for issue in result.issues:
            if issue.severity == "WARNING" and issue.rule_id == "WC-MOVABLE-W001":
                lines.append("WARNING")
                lines.append("MOVABLE_PATH_REFERENCE")
            lines.append(f"{issue.severity} [{issue.rule_id}] {issue.message}")

    lines.extend(
        [
            "",
            "Result:",
            f"{result.error_count} ERROR",
            f"{result.warning_count} WARNING",
            "",
        ]
    )
    return "\n".join(lines)
