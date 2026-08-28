"""Pure Generated dossier rendering."""

from __future__ import annotations

import hashlib

from .constants import CONTRACT_VERSION
from .models import ProjectDocumentSet
from .parser import parse_project
from pathlib import Path


def _fingerprint(parts: list[str]) -> str:
    payload = "\n".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def render_generated_dossier(docs: ProjectDocumentSet) -> str:
    assumption_refs = [item.ref for item in docs.assumptions]
    claim_refs = [item.ref for item in docs.claims]
    evidence_refs = [item.ref for item in docs.evidence]
    decision_refs = [item.ref for item in docs.decisions]
    negative_refs = [item.ref for item in docs.negative_results]
    lines = [
        f"contract_version: {CONTRACT_VERSION}",
        f"assumptions: {len(docs.assumptions)} ({', '.join(assumption_refs) or 'none'})",
        f"claims: {len(docs.claims)} ({', '.join(claim_refs) or 'none'})",
        f"evidence: {len(docs.evidence)} ({', '.join(evidence_refs) or 'none'})",
        f"decisions: {len(docs.decisions)} ({', '.join(decision_refs) or 'none'})",
        f"negative_results: {len(docs.negative_results)} ({', '.join(negative_refs) or 'none'})",
        f"literature: {len(docs.literature)} ({', '.join(item.ref for item in docs.literature) or 'none'})",
        f"novelty: {len(docs.novelty)} ({', '.join(item.ref for item in docs.novelty) or 'none'})",
        f"reviews: {len(docs.reviews)} ({', '.join(item.ref for item in docs.reviews) or 'none'})",
    ]
    if docs.governance is not None:
        lines.append(
            "governance: "
            f"{docs.governance.project_data_level}/"
            f"authorized={docs.governance.external_processing_authorized}/"
            f"{docs.governance.license_status}"
        )
    else:
        lines.append("governance: missing")

    next_steps: list[str] = []
    for claim in docs.claims:
        if not claim.evidence_refs:
            next_steps.append(f"Claim {claim.ref} has no Evidence")
    for item in docs.evidence:
        if not item.source_citation and not item.source_sha256 and not item.literature_ref:
            next_steps.append(
                f"Evidence {item.ref} is missing a stable citation or hash"
            )
    from .governance import assess_docs

    assessment = assess_docs(docs)
    if assessment.verdict == "BLOCKED":
        next_steps.append(
            "Governance external-processing preflight is BLOCKED"
        )
    for item in docs.assumptions:
        if item.status == "ACTIVE" and not item.impacts:
            next_steps.append(
                f"Active assumption {item.ref} is missing impact relations"
            )
    from .literature import citation_coverage, open_blocking_reviews, retraction_violations

    _, _, missing_cite = citation_coverage(docs)
    for ref in missing_cite:
        next_steps.append(f"Core claim {ref} is missing citable Evidence")
    for issue in retraction_violations(docs):
        next_steps.append(issue)
    for ref in open_blocking_reviews(docs):
        next_steps.append(f"Blocking review {ref} is OPEN")
    if docs.novelty:
        lines.append("novelty_matrix:")
        for item in docs.novelty:
            addition = ", ".join(item.addition_evidence_refs) or "none"
            lines.append(
                f"- {item.dimension}: existing={item.existing_work}; "
                f"current={item.current_work}; addition={addition}"
            )
    lines.append("next_step_candidates:")
    if next_steps:
        lines.extend(f"- {step}" for step in next_steps)
    else:
        lines.append("- none")

    fingerprint = _fingerprint(lines)
    lines.append(f"canonical_fingerprint: {fingerprint}")
    return "\n".join(lines) + "\n"


def render_generated_dossier_for_project(project: Path) -> str:
    return render_generated_dossier(parse_project(project))
