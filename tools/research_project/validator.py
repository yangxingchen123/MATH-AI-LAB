"""Read-only research project validator."""

from __future__ import annotations

from pathlib import Path

from .constants import DOSSIER_BEGIN, DOSSIER_END, REQUIRED_DIRS, REQUIRED_FILES
from .literature import hype_violations, retraction_violations, unsupported_attributions
from .models import ProjectDocumentSet, ResearchProjectValidationResult
from .parser import parse_project, serialize_record


def _dossier_markers_ok(text: str) -> tuple[bool, str]:
    begin_count = text.count(DOSSIER_BEGIN)
    end_count = text.count(DOSSIER_END)
    if begin_count != 1 or end_count != 1:
        return False, "research_dossier.md must contain exactly one Generated marker pair"
    begin_at = text.find(DOSSIER_BEGIN)
    end_at = text.find(DOSSIER_END)
    if begin_at < 0 or end_at < 0 or begin_at >= end_at:
        return False, "Generated dossier markers are damaged or mis-ordered"
    return True, ""


def _check_claim_evidence(docs: ProjectDocumentSet, errors: list[str]) -> None:
    claim_by_ref = {claim.ref: claim for claim in docs.claims}
    evidence_by_ref = {item.ref: item for item in docs.evidence}
    for item in docs.evidence:
        if item.claim_ref not in claim_by_ref:
            errors.append(f"{item.ref} claim_ref {item.claim_ref} does not exist")
            continue
        claim = claim_by_ref[item.claim_ref]
        if item.ref not in claim.evidence_refs:
            errors.append(f"{item.ref} is not listed on {claim.ref} evidence_refs")
    for claim in docs.claims:
        for ref in claim.evidence_refs:
            if ref not in evidence_by_ref:
                errors.append(f"{claim.ref} lists missing {ref}")
                continue
            if evidence_by_ref[ref].claim_ref != claim.ref:
                errors.append(
                    f"{ref} claim_ref {evidence_by_ref[ref].claim_ref} does not match {claim.ref}"
                )


def _check_assumption_links(docs: ProjectDocumentSet, errors: list[str]) -> None:
    by_ref = {item.ref: item for item in docs.assumptions}
    for item in docs.assumptions:
        if item.supersedes and item.supersedes not in by_ref:
            errors.append(f"{item.ref} supersedes missing {item.supersedes}")
        if item.superseded_by and item.superseded_by not in by_ref:
            errors.append(f"{item.ref} superseded_by missing {item.superseded_by}")
        if item.status == "SUPERSEDED" and not item.superseded_by:
            errors.append(f"{item.ref} SUPERSEDED must set superseded_by")
        if item.superseded_by:
            successor = by_ref.get(item.superseded_by)
            if successor is not None and successor.supersedes != item.ref:
                errors.append(
                    f"{item.ref} superseded_by {item.superseded_by} is not bidirectional"
                )


def _check_uniqueness(docs: ProjectDocumentSet, errors: list[str]) -> None:
    seen: dict[str, str] = {}
    bucket = (
        [(a.ref, "ASSUMPTION") for a in docs.assumptions]
        + [(c.ref, "CLAIM") for c in docs.claims]
        + [(e.ref, "EVIDENCE") for e in docs.evidence]
        + [(d.ref, "DECISION") for d in docs.decisions]
        + [(n.ref, "NEGATIVE_RESULT") for n in docs.negative_results]
        + [(x.ref, "AI_CONTRIBUTION") for x in docs.ai_contributions]
        + [(item.ref, "LITERATURE") for item in docs.literature]
        + [(item.ref, "NOVELTY") for item in docs.novelty]
        + [(item.ref, "REVIEW") for item in docs.reviews]
    )
    if docs.governance is not None:
        bucket.append((docs.governance.ref, "GOVERNANCE"))
    for ref, type_name in bucket:
        if ref in seen:
            errors.append(f"duplicate {ref}")
        else:
            seen[ref] = type_name
    if docs.governance is None:
        errors.append("missing GOVERNANCE GOV-0001")
    elif docs.governance.ref != "GOV-0001":
        errors.append("GOVERNANCE ref must be GOV-0001")


def _check_dossier_copy(docs: ProjectDocumentSet, errors: list[str]) -> None:
    dossier = docs.dossier_text
    if not dossier:
        return
    for records in docs.records_by_file.values():
        for record in records:
            raw = record.raw if record.raw else serialize_record(record)
            marker_line = (
                f"<!-- MATH-AI-LAB:RESEARCH-RECORD type={record.type} "
                f"ref={record.ref} BEGIN -->"
            )
            if marker_line in dossier and raw.strip() in dossier:
                errors.append(
                    f"research_dossier.md copies full record block for {record.ref}"
                )


def validate_project(project: Path) -> ResearchProjectValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    project = Path(project)
    for name in REQUIRED_FILES:
        if not (project / name).is_file():
            errors.append(f"missing required file: {name}")
    for name in REQUIRED_DIRS:
        if not (project / name).is_dir():
            errors.append(f"missing required directory: {name}")
    dossier_path = project / "research_dossier.md"
    if dossier_path.is_file():
        ok_markers, message = _dossier_markers_ok(
            dossier_path.read_text(encoding="utf-8")
        )
        if not ok_markers:
            errors.append(message)
    if any(item.startswith("missing required file:") for item in errors):
        return ResearchProjectValidationResult(ok=False, errors=errors, warnings=warnings)
    try:
        docs = parse_project(project)
    except ValueError as exc:
        errors.append(str(exc))
        return ResearchProjectValidationResult(ok=False, errors=errors, warnings=warnings)
    _check_uniqueness(docs, errors)
    _check_claim_evidence(docs, errors)
    _check_assumption_links(docs, errors)
    _check_dossier_copy(docs, errors)
    errors.extend(retraction_violations(docs))
    errors.extend(unsupported_attributions(docs))
    errors.extend(hype_violations(docs))
    lit_by_ref = {item.ref: item for item in docs.literature}
    for item in docs.evidence:
        if item.literature_ref and item.literature_ref not in lit_by_ref:
            errors.append(f"{item.ref} literature_ref {item.literature_ref} does not exist")
    evd_by_ref = {item.ref: item for item in docs.evidence}
    seen_dim: set[str] = set()
    for item in docs.novelty:
        if item.dimension in seen_dim:
            errors.append(f"duplicate novelty dimension {item.dimension}")
        seen_dim.add(item.dimension)
        for ref in item.addition_evidence_refs:
            if ref not in evd_by_ref:
                errors.append(f"{item.ref} addition_evidence_refs missing {ref}")
    return ResearchProjectValidationResult(
        ok=not errors,
        errors=errors,
        warnings=warnings,
    )
