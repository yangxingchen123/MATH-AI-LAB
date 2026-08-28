"""v1.3 literature evidence helpers. Not a Frozen Schema."""

from __future__ import annotations

from pathlib import Path

from .constants import (
    CORE_CLAIM_STATUSES,
    HYPE_TERMS,
    STATUS_REQUIRING_ACK,
)
from .models import LiteratureRecord, ProjectDocumentSet
from .parser import parse_records


def literature_to_bibtex(item: LiteratureRecord) -> str:
    key = item.ref.lower().replace("-", "")
    fields = [
        f"  title = {{{item.title}}}",
        f"  author = {{{item.authors}}}",
        f"  year = {{{item.year}}}",
    ]
    if item.venue:
        fields.append(f"  journal = {{{item.venue}}}")
    if item.doi:
        fields.append(f"  doi = {{{item.doi}}}")
    if item.url:
        fields.append(f"  url = {{{item.url}}}")
    return "@misc{" + key + ",\n" + ",\n".join(fields) + "\n}\n"


def literature_to_csl(item: LiteratureRecord) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": item.ref,
        "type": "article-journal" if item.venue else "document",
        "title": item.title,
        "author": [{"literal": item.authors}],
        "issued": {"date-parts": [[int(item.year)]]},
    }
    if item.doi:
        payload["DOI"] = item.doi
    if item.url:
        payload["URL"] = item.url
    if item.venue:
        payload["container-title"] = item.venue
    return payload


def is_core_claim(status: str, core: str | None) -> bool:
    if core == "false":
        return False
    if core == "true":
        return True
    return status in CORE_CLAIM_STATUSES


def evidence_has_citation(item) -> bool:
    return bool(item.source_citation or item.source_sha256 or item.literature_ref)


def citation_coverage(docs: ProjectDocumentSet) -> tuple[int, int, list[str]]:
    missing: list[str] = []
    core = [claim for claim in docs.claims if is_core_claim(claim.status, claim.core)]
    covered = 0
    evidence_by_ref = {item.ref: item for item in docs.evidence}
    for claim in core:
        cited = False
        for ref in claim.evidence_refs:
            item = evidence_by_ref.get(ref)
            if item is not None and evidence_has_citation(item):
                cited = True
                break
        if cited:
            covered += 1
        else:
            missing.append(claim.ref)
    return covered, len(core), missing


def unsupported_attributions(docs: ProjectDocumentSet) -> list[str]:
    issues: list[str] = []
    for item in docs.evidence:
        if item.kind in {"QUOTE", "PARAPHRASE"} and not evidence_has_citation(item):
            issues.append(f"{item.ref} {item.kind} lacks a stable source")
        if item.kind == "INFERENCE" and "文献证明" in item.body:
            issues.append(f"{item.ref} INFERENCE uses unsupported attribution")
    return issues


def retraction_violations(docs: ProjectDocumentSet) -> list[str]:
    by_ref = {item.ref: item for item in docs.literature}
    issues: list[str] = []
    for item in docs.evidence:
        if not item.literature_ref:
            continue
        lit = by_ref.get(item.literature_ref)
        if lit is None:
            issues.append(f"{item.ref} literature_ref {item.literature_ref} does not exist")
            continue
        if lit.publication_status in STATUS_REQUIRING_ACK:
            if item.acknowledges_status != "true":
                issues.append(
                    f"{item.ref} cites {lit.ref} ({lit.publication_status}) without acknowledges_status"
                )
    return issues


def hype_violations(docs: ProjectDocumentSet) -> list[str]:
    texts = [docs.dossier_text]
    for claim in docs.claims:
        texts.append(claim.body)
    for item in docs.novelty:
        texts.append(item.body)
        texts.append(item.current_work)
    blob = "\n".join(texts)
    found = [term for term in HYPE_TERMS if term in blob]
    if not found:
        return []
    verified = any(item.addition_evidence_refs for item in docs.novelty)
    if verified:
        return []
    return [
        f"novelty language {found} used without verifiable addition Evidence"
    ]


def open_blocking_reviews(docs: ProjectDocumentSet) -> list[str]:
    return [
        item.ref
        for item in docs.reviews
        if item.severity == "BLOCKING" and item.status == "OPEN"
    ]


def classify_fixture_rate(root: Path) -> tuple[int, int]:
    expected = {
        "quote.md": "QUOTE",
        "paraphrase.md": "PARAPHRASE",
        "inference.md": "INFERENCE",
    }
    correct = 0
    for name, kind in expected.items():
        path = root / name
        records = parse_records(path.read_text(encoding="utf-8"))
        if len(records) == 1 and records[0].metadata.get("kind") == kind:
            correct += 1
    return correct, len(expected)
