from pathlib import Path

import pytest

from tools.research_project.parser import (
    normalize_record_content,
    parse_local_ref,
    parse_project,
    parse_records,
)


def test_parse_local_ref_accepts_typed_ids():
    assert parse_local_ref("ASM-0001").prefix == "ASM"
    assert parse_local_ref("NEG-0012").number == 12
    assert parse_local_ref("GOV-0001").prefix == "GOV"
    assert parse_local_ref("AIC-0001").prefix == "AIC"


def test_parse_local_ref_rejects_gov_0002_and_attempt_ids():
    with pytest.raises(ValueError):
        parse_local_ref("GOV-0002")
    with pytest.raises(ValueError):
        parse_local_ref("A000001")


def test_parse_records_requires_separator_and_keeps_nested_body():
    block = (
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 BEGIN -->\n"
        "- status: ACTIVE\n"
        "- scope: s\n"
        "- rationale: r\n"
        "- falsifiable_when: f\n"
        "---\n"
        "## Nested heading must stay inside record\n"
        "- list item: with colon\n"
        "body continues\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 END -->\n"
    )
    records = parse_records(block)
    assert len(records) == 1
    assert "## Nested heading must stay inside record" in records[0].body
    assert "- list item: with colon" in records[0].body


def test_damage_matrix_fails(parse_should_fail_fixture):
    with pytest.raises(ValueError):
        parse_records(parse_should_fail_fixture)


def test_unknown_duplicate_empty_metadata_fails():
    bad = (
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 BEGIN -->\n"
        "- status: OPEN\n"
        "- status: OPEN\n"
        "---\n"
        "x\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 END -->\n"
    )
    with pytest.raises(ValueError):
        parse_records(bad)


def test_nfc_identity_for_equal_content():
    a = "café"
    b = "cafe\u0301"
    assert normalize_record_content(a) == normalize_record_content(b)


def test_parse_project_reads_template_governance():
    from tools.research_project.constants import TEMPLATE_ROOT

    docs = parse_project(TEMPLATE_ROOT)
    assert docs.governance is not None
    assert docs.governance.ref == "GOV-0001"


def test_legal_grammar_fixtures_parse():
    root = Path("tests/research_project/fixtures/grammar")
    for name in [
        "legal_assumption.md",
        "legal_claim.md",
        "legal_evidence.md",
        "legal_decision.md",
        "legal_negative_result.md",
        "legal_governance.md",
        "legal_ai_contribution.md",
        "nested_heading_body.md",
        "claim_and_evidence.md",
    ]:
        parse_records((root / name).read_text(encoding="utf-8"))
