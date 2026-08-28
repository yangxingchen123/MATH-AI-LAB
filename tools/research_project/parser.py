"""Parse Research Record Grammar (BEGIN/END + mandatory ---)."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .constants import (
    EXTERNAL_SOURCE_KINDS,
    FILE_ALLOWED_TYPES,
    IDENTITY_KIND_FIELDS,
    OPTIONAL_LEDGER_FILES,
    PREFIX_TYPE,
    REQUIRED_FILES,
    TYPE_ENUMS,
    TYPE_OPTIONAL_KEYS,
    TYPE_PREFIX,
    TYPE_REQUIRED_KEYS,
)
from .models import (
    AiContributionRecord,
    AssumptionRecord,
    ClaimRecord,
    DecisionRecord,
    EvidenceRecord,
    GovernanceRecord,
    LiteratureRecord,
    LocalRef,
    NegativeResultRecord,
    NoveltyRecord,
    ProjectDocumentSet,
    ResearchRecord,
    ReviewRecord,
)

MARKER_RE = re.compile(
    r"<!-- MATH-AI-LAB:RESEARCH-RECORD type=(?P<type>[A-Z_]+) "
    r"ref=(?P<ref>[A-Z]+-\d{4}) (?P<kind>BEGIN|END) -->"
)
LOCAL_REF_RE = re.compile(r"^([A-Z]+)-(\d{4})$")
META_LINE_RE = re.compile(r"^- ([a-z_]+): (.+)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
YEAR_RE = re.compile(r"^\d{4}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def normalize_record_content(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def parse_local_ref(text: str) -> LocalRef:
    raw = text.strip()
    match = LOCAL_REF_RE.fullmatch(raw)
    if match is None:
        raise ValueError(f"illegal local ref: {text!r}")
    prefix, number_text = match.group(1), match.group(2)
    if prefix not in PREFIX_TYPE:
        raise ValueError(f"unknown local ref prefix: {prefix}")
    number = int(number_text)
    if prefix == "GOV" and number != 1:
        raise ValueError("GOVERNANCE ref must be GOV-0001")
    return LocalRef(prefix=prefix, number=number, text=raw)


def _parse_list(value: str | None) -> list[str]:
    if value is None or not value.strip():
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def serialize_record(record: ResearchRecord) -> str:
    lines = [
        f"<!-- MATH-AI-LAB:RESEARCH-RECORD type={record.type} ref={record.ref} BEGIN -->"
    ]
    for key, value in record.metadata.items():
        lines.append(f"- {key}: {value}")
    body = record.body
    if body.endswith("\n"):
        body_out = body
    else:
        body_out = body + "\n"
    block = "\n".join(lines) + "\n---\n" + body_out
    if not block.endswith("\n"):
        block += "\n"
    block += (
        f"<!-- MATH-AI-LAB:RESEARCH-RECORD type={record.type} ref={record.ref} END -->\n"
    )
    return block


def canonical_record_content(record: ResearchRecord) -> str:
    meta = "\n".join(
        f"{key}:{normalize_record_content(value)}"
        for key, value in record.metadata.items()
    )
    return normalize_record_content(
        f"{record.type}\n{record.ref}\n{meta}\n{record.body}"
    )


def _validate_metadata(type_name: str, metadata: dict[str, str]) -> None:
    required = TYPE_REQUIRED_KEYS[type_name]
    optional = TYPE_OPTIONAL_KEYS[type_name]
    allowed = set(required) | set(optional)
    missing = [key for key in required if key not in metadata]
    if missing:
        raise ValueError(f"{type_name} missing required keys: {', '.join(missing)}")
    unknown = [key for key in metadata if key not in allowed]
    if unknown:
        raise ValueError(f"{type_name} unknown keys: {', '.join(unknown)}")
    enums = TYPE_ENUMS.get(type_name, {})
    for key, allowed_values in enums.items():
        if key in metadata and metadata[key] not in allowed_values:
            raise ValueError(
                f"{type_name} {key} has illegal value {metadata[key]!r}"
            )
    if type_name == "DECISION" and "date" in metadata:
        if DATE_RE.fullmatch(metadata["date"]) is None:
            raise ValueError(f"illegal decision date: {metadata['date']!r}")
    if type_name == "AI_CONTRIBUTION" and "date" in metadata:
        if DATE_RE.fullmatch(metadata["date"]) is None:
            raise ValueError(f"illegal AI contribution date: {metadata['date']!r}")
    if type_name == "EVIDENCE":
        kind = metadata.get("kind")
        if kind in EXTERNAL_SOURCE_KINDS:
            if not (
                metadata.get("source_citation")
                or metadata.get("source_sha256")
                or metadata.get("literature_ref")
            ):
                raise ValueError(
                    "QUOTE/PARAPHRASE evidence requires source_citation, "
                    "source_sha256, or literature_ref"
                )
        sha = metadata.get("source_sha256")
        if sha is not None and SHA256_RE.fullmatch(sha) is None:
            raise ValueError("source_sha256 must be 64 lowercase hex characters")
        lit = metadata.get("literature_ref")
        if lit is not None:
            parsed = parse_local_ref(lit)
            if parsed.prefix != "LIT":
                raise ValueError("literature_ref must be a LIT-#### ref")
    if type_name == "LITERATURE":
        if YEAR_RE.fullmatch(metadata["year"]) is None:
            raise ValueError(f"illegal literature year: {metadata['year']!r}")
        field_name = IDENTITY_KIND_FIELDS[metadata["identity_kind"]]
        if not metadata.get(field_name):
            raise ValueError(
                f"LITERATURE identity_kind {metadata['identity_kind']} requires {field_name}"
            )
        sha = metadata.get("source_sha256")
        if sha is not None and SHA256_RE.fullmatch(sha) is None:
            raise ValueError("source_sha256 must be 64 lowercase hex characters")
        if metadata.get("accessed_at") and DATE_RE.fullmatch(metadata["accessed_at"]) is None:
            raise ValueError(f"illegal accessed_at: {metadata['accessed_at']!r}")
    if type_name == "REVIEW" and metadata.get("status") == "WAIVED":
        if not metadata.get("waiver_reason"):
            raise ValueError("WAIVED review requires waiver_reason")


def parse_records(text: str) -> list[ResearchRecord]:
    matches = list(MARKER_RE.finditer(text))
    records: list[ResearchRecord] = []
    stack: list[tuple[str, str, int, int]] = []

    for match in matches:
        type_name = match.group("type")
        ref = match.group("ref")
        kind = match.group("kind")
        if kind == "BEGIN":
            if stack:
                raise ValueError("nested or duplicate BEGIN marker")
            stack.append((type_name, ref, match.start(), match.end()))
            continue
        if not stack:
            raise ValueError("orphan END marker")
        begin_type, begin_ref, begin_start, begin_end = stack.pop()
        if begin_type != type_name or begin_ref != ref:
            raise ValueError("BEGIN/END type-ref mismatch")
        inner = text[begin_end : match.start()]
        if "\n---\n" not in inner:
            raise ValueError("missing mandatory --- metadata/body separator")
        meta_text, body = inner.split("\n---\n", 1)
        metadata: dict[str, str] = {}
        for line in meta_text.splitlines():
            if line.strip() == "":
                continue
            meta_match = META_LINE_RE.fullmatch(line)
            if meta_match is None:
                raise ValueError(f"illegal metadata line: {line!r}")
            key, value = meta_match.group(1), meta_match.group(2)
            if key in metadata:
                raise ValueError(f"duplicate metadata key: {key}")
            if value == "":
                raise ValueError(f"empty metadata value for {key}")
            metadata[key] = value
        if type_name not in TYPE_PREFIX:
            raise ValueError(f"unknown record type: {type_name}")
        local = parse_local_ref(ref)
        expected_prefix = TYPE_PREFIX[type_name]
        if local.prefix != expected_prefix:
            raise ValueError(f"type {type_name} requires prefix {expected_prefix}")
        _validate_metadata(type_name, metadata)
        raw = text[begin_start : match.end()]
        if not raw.endswith("\n"):
            raw = raw + "\n"
        records.append(
            ResearchRecord(
                type=type_name,
                ref=ref,
                metadata=metadata,
                body=body,
                raw=raw if text[begin_start : match.end()].endswith("\n") else raw,
            )
        )
    if stack:
        raise ValueError("missing END marker")
    return records


def split_preamble_and_records(text: str) -> tuple[str, list[ResearchRecord]]:
    records = parse_records(text)
    if not records:
        return text, []
    first = MARKER_RE.search(text)
    assert first is not None
    return text[: first.start()], records


def render_file(preamble: str, records: list[ResearchRecord]) -> str:
    parts = [preamble]
    if preamble and not preamble.endswith("\n"):
        parts[0] = preamble + "\n"
    chunks: list[str] = []
    if parts[0]:
        chunks.append(parts[0] if parts[0].endswith("\n") else parts[0] + "\n")
    for record in records:
        block = record.raw if record.raw else serialize_record(record)
        if not block.endswith("\n"):
            block += "\n"
        if chunks and not chunks[-1].endswith("\n"):
            chunks[-1] += "\n"
        chunks.append(block)
    text = "".join(chunks)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def _typed_assumption(record: ResearchRecord) -> AssumptionRecord:
    md = record.metadata
    return AssumptionRecord(
        ref=record.ref,
        status=md["status"],
        scope=md["scope"],
        rationale=md["rationale"],
        falsifiable_when=md["falsifiable_when"],
        body=record.body,
        impacts=_parse_list(md.get("impacts")),
        supersedes=md.get("supersedes"),
        superseded_by=md.get("superseded_by"),
        reviewed=md.get("reviewed"),
        record=record,
    )


def _typed_claim(record: ResearchRecord) -> ClaimRecord:
    md = record.metadata
    return ClaimRecord(
        ref=record.ref,
        status=md["status"],
        body=record.body,
        evidence_refs=_parse_list(md.get("evidence_refs")),
        core=md.get("core"),
        record=record,
    )


def _typed_evidence(record: ResearchRecord) -> EvidenceRecord:
    md = record.metadata
    return EvidenceRecord(
        ref=record.ref,
        claim_ref=md["claim_ref"],
        polarity=md["polarity"],
        kind=md["kind"],
        body=record.body,
        source_citation=md.get("source_citation"),
        source_sha256=md.get("source_sha256"),
        literature_ref=md.get("literature_ref"),
        acknowledges_status=md.get("acknowledges_status"),
        record=record,
    )


def _typed_decision(record: ResearchRecord) -> DecisionRecord:
    md = record.metadata
    return DecisionRecord(
        ref=record.ref,
        date=md["date"],
        question=md["question"],
        options=md["options"],
        choice=md["choice"],
        basis=md["basis"],
        cost=md["cost"],
        reversible=md["reversible"],
        revisit_when=md["revisit_when"],
        body=record.body,
        opposes=_parse_list(md.get("opposes")),
        evidence_refs=_parse_list(md.get("evidence_refs")),
        supersedes=md.get("supersedes"),
        record=record,
    )


def _typed_negative(record: ResearchRecord) -> NegativeResultRecord:
    md = record.metadata
    return NegativeResultRecord(
        ref=record.ref,
        status=md["status"],
        failed_route=md["failed_route"],
        failure_evidence_refs=_parse_list(md["failure_evidence_refs"]),
        impact=md["impact"],
        retry_when=md["retry_when"],
        body=record.body,
        related_claims=_parse_list(md.get("related_claims")),
        related_decisions=_parse_list(md.get("related_decisions")),
        record=record,
    )


def _typed_governance(record: ResearchRecord) -> GovernanceRecord:
    md = record.metadata
    return GovernanceRecord(
        ref=record.ref,
        project_data_level=md["project_data_level"],
        external_processing_authorized=md["external_processing_authorized"],
        license_status=md["license_status"],
        body=record.body,
        notes=md.get("notes"),
        record=record,
    )


def _typed_aic(record: ResearchRecord) -> AiContributionRecord:
    md = record.metadata
    return AiContributionRecord(
        ref=record.ref,
        date=md["date"],
        role=md["role"],
        summary=md["summary"],
        human_review=md["human_review"],
        body=record.body,
        tools=md.get("tools"),
        record=record,
    )


def _typed_literature(record: ResearchRecord) -> LiteratureRecord:
    md = record.metadata
    return LiteratureRecord(
        ref=record.ref,
        title=md["title"],
        authors=md["authors"],
        year=md["year"],
        identity_kind=md["identity_kind"],
        publication_status=md["publication_status"],
        body=record.body,
        doi=md.get("doi"),
        isbn=md.get("isbn"),
        arxiv=md.get("arxiv"),
        venue=md.get("venue"),
        version=md.get("version"),
        url=md.get("url"),
        accessed_at=md.get("accessed_at"),
        source_sha256=md.get("source_sha256"),
        license_status=md.get("license_status"),
        supersedes=md.get("supersedes"),
        notes=md.get("notes"),
        record=record,
    )


def _typed_novelty(record: ResearchRecord) -> NoveltyRecord:
    md = record.metadata
    return NoveltyRecord(
        ref=record.ref,
        dimension=md["dimension"],
        existing_work=md["existing_work"],
        current_work=md["current_work"],
        addition_evidence_refs=_parse_list(md.get("addition_evidence_refs")),
        body=record.body,
        notes=md.get("notes"),
        record=record,
    )


def _typed_review(record: ResearchRecord) -> ReviewRecord:
    md = record.metadata
    return ReviewRecord(
        ref=record.ref,
        role=md["role"],
        severity=md["severity"],
        status=md["status"],
        target_ref=md["target_ref"],
        body=record.body,
        disposition=md.get("disposition"),
        waiver_reason=md.get("waiver_reason"),
        record=record,
    )


def parse_project(project: Path) -> ProjectDocumentSet:
    docs = ProjectDocumentSet()
    dossier_path = project / "research_dossier.md"
    if dossier_path.is_file():
        docs.dossier_text = dossier_path.read_text(encoding="utf-8")
    ledger_files = [
        name for name in REQUIRED_FILES if name != "research_dossier.md"
    ] + list(OPTIONAL_LEDGER_FILES)
    for filename in ledger_files:
        path = project / filename
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        preamble, records = split_preamble_and_records(text)
        allowed = FILE_ALLOWED_TYPES[filename]
        for record in records:
            if record.type not in allowed:
                raise ValueError(
                    f"{filename} contains disallowed type {record.type} ref={record.ref}"
                )
        docs.preambles[filename] = preamble
        docs.records_by_file[filename] = records
        for record in records:
            if record.type == "ASSUMPTION":
                docs.assumptions.append(_typed_assumption(record))
            elif record.type == "CLAIM":
                docs.claims.append(_typed_claim(record))
            elif record.type == "EVIDENCE":
                docs.evidence.append(_typed_evidence(record))
            elif record.type == "DECISION":
                docs.decisions.append(_typed_decision(record))
            elif record.type == "NEGATIVE_RESULT":
                docs.negative_results.append(_typed_negative(record))
            elif record.type == "GOVERNANCE":
                if docs.governance is not None:
                    raise ValueError("multiple GOVERNANCE records")
                docs.governance = _typed_governance(record)
            elif record.type == "AI_CONTRIBUTION":
                docs.ai_contributions.append(_typed_aic(record))
            elif record.type == "LITERATURE":
                docs.literature.append(_typed_literature(record))
            elif record.type == "NOVELTY":
                docs.novelty.append(_typed_novelty(record))
            elif record.type == "REVIEW":
                docs.reviews.append(_typed_review(record))
    return docs


def replace_record_metadata(record: ResearchRecord, updates: dict[str, str]) -> ResearchRecord:
    metadata = dict(record.metadata)
    for key, value in updates.items():
        if value == "":
            metadata.pop(key, None)
        else:
            metadata[key] = value
    updated = ResearchRecord(
        type=record.type,
        ref=record.ref,
        metadata=metadata,
        body=record.body,
        raw="",
    )
    _validate_metadata(updated.type, updated.metadata)
    updated.raw = serialize_record(updated)
    return updated
