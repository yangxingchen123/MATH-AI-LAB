"""Deterministic research-project reports."""

from __future__ import annotations

from .models import (
    ExternalProcessingAssessment,
    ResearchProjectOperationResult,
    ResearchProjectStatusResult,
    ResearchProjectValidationResult,
)


def format_validation(result: ResearchProjectValidationResult) -> str:
    if result.ok:
        return "PASS\n"
    lines = ["FAIL"]
    lines.extend(f"ERROR: {item}" for item in result.errors)
    lines.extend(f"WARNING: {item}" for item in result.warnings)
    return "\n".join(lines) + "\n"


def format_operation(result: ResearchProjectOperationResult) -> str:
    return f"{result.kind.value}: {result.message}\n"


def format_status(result: ResearchProjectStatusResult) -> str:
    required = "true" if result.reconcile_required else "false"
    return (
        f"project: {result.project}\n"
        f"freshness: {result.freshness}\n"
        f"reconcile_required: {required}\n"
        f"external_processing: {result.external_processing}\n"
        f"contract_version: {result.contract_version}\n"
    )


def format_assessment(result: ExternalProcessingAssessment) -> str:
    reasons = ",".join(result.reason_codes) if result.reason_codes else "none"
    return f"{result.verdict} ({reasons}): {result.message}\n"
