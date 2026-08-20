"""Inspect compiler output and classify blocking errors vs warnings."""

from __future__ import annotations

import re

from .models import BuildIssue, CompileResult, InspectionResult, IssueSeverity

_FATAL_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"! Emergency stop", "LATEX_EMERGENCY_STOP"),
    (r"! LaTeX Error:", "LATEX_FATAL_ERROR"),
    (r"Undefined control sequence", "UNDEFINED_CONTROL_SEQUENCE"),
    (r"Fatal error occurred", "LATEX_FATAL_ERROR"),
)

_UNDEFINED_REF = re.compile(r"LaTeX Warning: There were undefined references", re.IGNORECASE)
_UNDEFINED_CITE = re.compile(r"LaTeX Warning: There were undefined citations", re.IGNORECASE)
_OVERFULL = re.compile(r"Overfull \\[hv]box", re.IGNORECASE)
_UNDERFULL = re.compile(r"Underfull \\[hv]box", re.IGNORECASE)
_LATEX_WARNING = re.compile(r"LaTeX Warning:", re.IGNORECASE)


def inspect_compile(compile_result: CompileResult) -> InspectionResult:
    blocking: list[BuildIssue] = []
    warnings: list[BuildIssue] = []
    log = compile_result.log_text

    if compile_result.return_code != 0:
        blocking.append(
            BuildIssue(
                severity=IssueSeverity.ERROR,
                code="COMPILER_NONZERO_EXIT",
                message=f"Compiler exited with code {compile_result.return_code}",
            )
        )

    if compile_result.built_pdf is None or not compile_result.built_pdf.is_file():
        blocking.append(
            BuildIssue(
                severity=IssueSeverity.ERROR,
                code="OUTPUT_PDF_MISSING",
                message="Built PDF missing from isolated build directory",
            )
        )
    elif compile_result.built_pdf.stat().st_size == 0:
        blocking.append(
            BuildIssue(
                severity=IssueSeverity.ERROR,
                code="OUTPUT_PDF_EMPTY",
                message="Built PDF is empty",
            )
        )

    for pattern, code in _FATAL_PATTERNS:
        if re.search(pattern, log):
            blocking.append(
                BuildIssue(
                    severity=IssueSeverity.ERROR,
                    code=code,
                    message=f"Detected in log: {pattern}",
                )
            )

    if _UNDEFINED_REF.search(log):
        blocking.append(
            BuildIssue(
                severity=IssueSeverity.ERROR,
                code="UNDEFINED_REFERENCES",
                message="Final log contains undefined references",
            )
        )

    if _UNDEFINED_CITE.search(log):
        blocking.append(
            BuildIssue(
                severity=IssueSeverity.ERROR,
                code="UNDEFINED_CITATIONS",
                message="Final log contains undefined citations",
            )
        )

    for idx, line in enumerate(log.splitlines(), start=1):
        if _OVERFULL.search(line):
            warnings.append(
                BuildIssue(
                    severity=IssueSeverity.WARNING,
                    code="OVERFULL_BOX",
                    message=line.strip(),
                    line=idx,
                )
            )
        elif _UNDERFULL.search(line):
            warnings.append(
                BuildIssue(
                    severity=IssueSeverity.WARNING,
                    code="UNDERFULL_BOX",
                    message=line.strip(),
                    line=idx,
                )
            )
        elif _LATEX_WARNING.search(line) and not _UNDEFINED_REF.search(line) and not _UNDEFINED_CITE.search(line):
            warnings.append(
                BuildIssue(
                    severity=IssueSeverity.WARNING,
                    code="LATEX_WARNING",
                    message=line.strip(),
                    line=idx,
                )
            )

    for issue in compile_result.issues:
        if issue.severity == IssueSeverity.ERROR:
            blocking.append(issue)
        else:
            warnings.append(issue)

    return InspectionResult(
        blocking_errors=tuple(blocking),
        warnings=tuple(warnings),
    )
