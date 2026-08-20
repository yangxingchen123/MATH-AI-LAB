"""Human-readable verification report."""

from __future__ import annotations

from .models import VerificationRunResult, VerificationStatus

_LAYER_ORDER: tuple[str, ...] = (
    "SOURCE INTEGRITY",
    "DERIVED INTEGRITY",
    "SOFTWARE INTEGRITY",
    "ARTIFACT INTEGRITY",
)


def format_report(run: VerificationRunResult, *, verbose: bool = False) -> str:
    lines = [
        "MATH-AI-LAB Verification",
        "",
        f"Profile: {run.profile}",
        "",
    ]
    if verbose and run.environment:
        lines.append("Environment")
        for key, value in run.environment.items():
            lines.append(f"{key:<22} {value}")
        lines.append("")

    by_layer: dict[str, list] = {}
    for check in run.checks:
        by_layer.setdefault(check.layer or "OTHER", []).append(check)

    for layer in _LAYER_ORDER:
        items = by_layer.get(layer)
        if not items:
            continue
        lines.append(layer)
        for check in items:
            lines.append(f"{check.name:<24} {check.status.value}")
            if check.status in (VerificationStatus.FAIL, VerificationStatus.BLOCKED):
                if check.category:
                    lines.append(f"{'Category':<24} {check.category.value}")
                if check.summary:
                    lines.append(f"{'Summary':<24} {check.summary}")
                if check.suggested_action:
                    lines.append(f"{'Suggested Action':<24} {check.suggested_action}")
            elif verbose:
                if check.summary:
                    lines.append(f"{'Summary':<24} {check.summary}")
                lines.append(f"{'Duration':<24} {check.duration_seconds:.2f} s")
                if check.details:
                    lines.append("Details")
                    for detail_line in check.details.splitlines()[:20]:
                        lines.append(f"  {detail_line}")
        lines.append("")

    lines.extend(
        [
            f"{'Overall':<24} {run.overall_status.value}",
            f"{'Elapsed':<24} {run.duration_seconds:.2f} s",
            "",
        ]
    )
    return "\n".join(lines)


def exit_code(run: VerificationRunResult) -> int:
    if run.overall_status in (VerificationStatus.PASS, VerificationStatus.PASS_WITH_WARNINGS):
        return 0
    if run.overall_status == VerificationStatus.SKIPPED:
        return 0
    return 1
