"""Human-readable report for LaTeX build."""

from __future__ import annotations

from .models import LatexBuildResult, PublishStatus


def format_report(result: LatexBuildResult, *, mode: str) -> str:
    compile_ok = result.compile_result.success and result.inspection_result.publish_allowed
    lines = [
        "MATH-AI-LAB LaTeX Build",
        "",
        f"Mode: {mode}",
        f"Project: {result.project.project_dir}",
        f"Source: {result.project.main_tex}",
        f"Compiler: {result.compile_result.compiler}",
        f"Runs: {result.compile_result.compiler_runs}",
        "",
        f"Compile: {'PASS' if result.compile_result.success else 'FAIL'}",
    ]
    if result.inspection_result.publish_allowed:
        inspect_line = "PASS"
        if result.warning_count:
            inspect_line = "PASS WITH WARNINGS"
        lines.append(f"Inspection: {inspect_line}")
    else:
        lines.append("Inspection: BLOCKED")

    lines.extend(
        [
            f"Blocking errors: {result.blocking_error_count}",
            f"Warnings: {result.warning_count}",
            "",
            f"Built PDF: {result.compile_result.built_pdf or '—'}",
            f"Formal PDF: {result.project.formal_pdf}",
            "",
        ]
    )

    if mode == "build" and result.publish_result is not None:
        pr = result.publish_result
        lines.extend(
            [
                f"Publish: {pr.status.value}",
                f"Writes: {pr.writes}",
            ]
        )
    else:
        lines.append("Publish: SKIPPED")

    if result.inspection_result.blocking_errors:
        lines.append("")
        lines.append("Blocking issues:")
        for issue in result.inspection_result.blocking_errors:
            lines.append(f"  [{issue.code}] {issue.message}")

    if result.inspection_result.warnings[:5]:
        lines.append("")
        lines.append("Warnings (first 5):")
        for issue in result.inspection_result.warnings[:5]:
            lines.append(f"  [{issue.code}] {issue.message}")

    overall = "PASS"
    if not compile_ok:
        overall = "BLOCKED"
    elif result.warning_count:
        overall = "PASS WITH WARNINGS"
    lines.extend(["", f"Result: {overall}"])
    return "\n".join(lines)


def exit_code(result: LatexBuildResult) -> int:
    if not result.inspection_result.publish_allowed:
        return 1
    if result.publish_result is not None and result.publish_result.status == PublishStatus.BLOCKED:
        return 1
    return 0
