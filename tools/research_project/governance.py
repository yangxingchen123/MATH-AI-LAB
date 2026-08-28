"""PROJECT_POLICY_PREFLIGHT external-processing assessment."""

from __future__ import annotations

from pathlib import Path

from .models import ExternalProcessingAssessment, ProjectDocumentSet
from .parser import parse_project


def assess_docs(docs: ProjectDocumentSet) -> ExternalProcessingAssessment:
    gov = docs.governance
    if gov is None:
        return ExternalProcessingAssessment(
            verdict="BLOCKED",
            reason_codes=("GOVERNANCE_MISSING",),
            message="Governance record is missing",
        )
    if gov.external_processing_authorized != "true":
        return ExternalProcessingAssessment(
            verdict="BLOCKED",
            reason_codes=("UNAUTHORIZED",),
            message="external_processing_authorized is false",
        )
    if gov.project_data_level == "RESTRICTED":
        return ExternalProcessingAssessment(
            verdict="BLOCKED",
            reason_codes=("RESTRICTED",),
            message="RESTRICTED data is blocked in v1.1",
        )
    if gov.project_data_level == "PERSONAL":
        return ExternalProcessingAssessment(
            verdict="BLOCKED",
            reason_codes=("PERSONAL",),
            message="PERSONAL data is blocked in v1.1",
        )
    if gov.project_data_level == "PUBLIC":
        if gov.license_status == "VERIFIED_FOR_EXTERNAL_PROCESSING":
            return ExternalProcessingAssessment(
                verdict="ALLOWED",
                reason_codes=("PROJECT_POLICY_PREFLIGHT",),
                message="project-level preflight allowed",
            )
        return ExternalProcessingAssessment(
            verdict="BLOCKED",
            reason_codes=("LICENSE_NOT_VERIFIED",),
            message="PUBLIC data requires VERIFIED_FOR_EXTERNAL_PROCESSING",
        )
    return ExternalProcessingAssessment(
        verdict="BLOCKED",
        reason_codes=("GOVERNANCE_ILLEGAL",),
        message="Governance record is illegal",
    )


def assess_external_processing(project: Path) -> ExternalProcessingAssessment:
    try:
        docs = parse_project(project)
    except ValueError as exc:
        return ExternalProcessingAssessment(
            verdict="BLOCKED",
            reason_codes=("GOVERNANCE_ILLEGAL",),
            message=str(exc),
        )
    return assess_docs(docs)
