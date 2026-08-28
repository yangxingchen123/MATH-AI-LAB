from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import (
    add_assumption,
    add_claim,
    add_evidence,
    append_decision,
    record_negative_result,
    supersede_assumption,
)
from tools.research_project.parser import parse_project
from tools.research_project.validator import validate_project


def test_add_assumption_atomic_success(tmp_project, candidate_asm):
    result = add_assumption(tmp_project, candidate_asm)
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    assert "ASM-0001" in (tmp_project / "assumptions.md").read_text(encoding="utf-8")


def test_add_assumption_rolls_back_on_invalid_candidate(tmp_project, bad_candidate):
    before = (tmp_project / "assumptions.md").read_bytes()
    result = add_assumption(tmp_project, bad_candidate)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert (tmp_project / "assumptions.md").read_bytes() == before


def test_same_ref_same_content_is_noop(tmp_project, candidate_asm):
    assert add_assumption(tmp_project, candidate_asm).kind == ResearchProjectOperationKind.WRITTEN
    assert add_assumption(tmp_project, candidate_asm).kind == ResearchProjectOperationKind.NO_OP


def test_same_ref_different_content_rejected(tmp_project, candidate_asm, candidate_asm_conflict):
    assert add_assumption(tmp_project, candidate_asm).kind == ResearchProjectOperationKind.WRITTEN
    before = (tmp_project / "assumptions.md").read_bytes()
    result = add_assumption(tmp_project, candidate_asm_conflict)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert (tmp_project / "assumptions.md").read_bytes() == before


def test_claim_evidence_loop_updates_backlink(tmp_project, candidate_clm_no_refs, candidate_evd):
    r1 = add_claim(tmp_project, candidate_clm_no_refs)
    assert r1.kind == ResearchProjectOperationKind.WRITTEN
    r2 = add_evidence(tmp_project, candidate_evd)
    assert r2.kind == ResearchProjectOperationKind.WRITTEN
    docs = parse_project(tmp_project)
    assert docs.claims[0].evidence_refs == ["EVD-0001"]
    assert docs.evidence[0].claim_ref == "CLM-0001"
    assert docs.claims[0].status == "OPEN"
    assert validate_project(tmp_project).ok is True


def test_add_evidence_failure_leaves_evidence_bytes_unchanged(
    tmp_project, candidate_clm_no_refs, candidate_evd_missing_kind
):
    assert add_claim(tmp_project, candidate_clm_no_refs).kind == ResearchProjectOperationKind.WRITTEN
    before = (tmp_project / "evidence.md").read_bytes()
    result = add_evidence(tmp_project, candidate_evd_missing_kind)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert (tmp_project / "evidence.md").read_bytes() == before


def test_candidate_must_not_be_official_path(tmp_project):
    official = tmp_project / "assumptions.md"
    result = add_assumption(tmp_project, official)
    assert result.kind == ResearchProjectOperationKind.REJECTED


def test_supersede_assumption_keeps_history(tmp_project, candidate_asm, candidate_replacement):
    assert add_assumption(tmp_project, candidate_asm).kind == ResearchProjectOperationKind.WRITTEN
    result = supersede_assumption(tmp_project, "ASM-0001", candidate_replacement)
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    text = (tmp_project / "assumptions.md").read_text(encoding="utf-8")
    assert "ASM-0001" in text and "SUPERSEDED" in text
    assert "ASM-0002" in text
    normalized = text.lower().replace(" ", "")
    assert "supersedes:asm-0001" in normalized
    assert "superseded_by:asm-0002" in normalized


def test_record_negative_result_requires_retry_condition(tmp_project, candidate_neg_incomplete):
    before = (tmp_project / "negative_results.md").read_bytes()
    result = record_negative_result(tmp_project, candidate_neg_incomplete)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert before == (tmp_project / "negative_results.md").read_bytes()


def test_record_negative_result_writes_canonical_block(tmp_project, candidate_neg_ok):
    result = record_negative_result(tmp_project, candidate_neg_ok)
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    text = (tmp_project / "negative_results.md").read_text(encoding="utf-8")
    assert "type=NEGATIVE_RESULT ref=NEG-0001" in text


def test_append_decision_writes_record(tmp_project, candidate_dec):
    result = append_decision(tmp_project, candidate_dec)
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    assert "DEC-0001" in (tmp_project / "decisions.md").read_text(encoding="utf-8")
