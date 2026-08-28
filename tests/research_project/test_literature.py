from pathlib import Path

from tools.research_project.literature import literature_to_bibtex
from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import (
    add_claim,
    add_evidence,
    add_literature,
    add_novelty,
    add_review,
)
from tools.research_project.parser import parse_project, parse_records
from tools.research_project.validator import validate_project


def test_legal_literature_parses():
    text = Path("tests/research_project/fixtures/grammar/legal_literature.md").read_text(
        encoding="utf-8"
    )
    records = parse_records(text)
    assert records[0].ref == "LIT-0001"
    assert "doi" in records[0].metadata


def test_retracted_unacked_fails_validate():
    project = Path("tests/research_project/fixtures/literature/retracted_unacked")
    result = validate_project(project)
    assert result.ok is False
    assert any("RETRACTED" in item or "acknowledges_status" in item for item in result.errors)


def test_retracted_acked_passes_validate():
    project = Path("tests/research_project/fixtures/literature/retracted_acked")
    assert validate_project(project).ok is True


def test_cited_core_claim_coverage_complete():
    from tools.research_project.literature import citation_coverage

    project = Path("tests/research_project/fixtures/literature/cited_core_claim")
    docs = parse_project(project)
    covered, total, missing = citation_coverage(docs)
    assert total == 1
    assert covered == 1
    assert missing == []
    assert validate_project(project).ok is True
    bib = literature_to_bibtex(docs.literature[0])
    assert "10.1000/example" in bib


def test_hype_without_novelty_blocked():
    project = Path("tests/research_project/fixtures/literature/hype_without_novelty")
    result = validate_project(project)
    assert result.ok is False
    assert any("首次" in item or "novelty language" in item for item in result.errors)


def test_hype_with_novelty_allowed():
    project = Path("tests/research_project/fixtures/literature/hype_with_novelty")
    assert validate_project(project).ok is True


def test_add_literature_and_review(tmp_project):
    lit = Path("tests/research_project/fixtures/candidates/lit_0001.md")
    assert add_literature(tmp_project, lit).kind == ResearchProjectOperationKind.WRITTEN
    docs = parse_project(tmp_project)
    assert docs.literature[0].ref == "LIT-0001"
    rev = Path("tests/research_project/fixtures/candidates/rev_0001.md")
    assert add_review(tmp_project, rev).kind == ResearchProjectOperationKind.WRITTEN
    assert "REV-0001" in (tmp_project / "reviews" / "reviews.md").read_text(encoding="utf-8")


def test_add_novelty_requires_existing_evidence(tmp_project, candidate_clm_no_refs, candidate_evd):
    nov = Path("tests/research_project/fixtures/candidates/nov_0001.md")
    before = (
        (tmp_project / "novelty.md").read_bytes()
        if (tmp_project / "novelty.md").is_file()
        else b""
    )
    result = add_novelty(tmp_project, nov)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert add_claim(tmp_project, candidate_clm_no_refs).kind == ResearchProjectOperationKind.WRITTEN
    assert add_evidence(tmp_project, candidate_evd).kind == ResearchProjectOperationKind.WRITTEN
    assert add_novelty(tmp_project, nov).kind == ResearchProjectOperationKind.WRITTEN
    if before:
        assert (tmp_project / "novelty.md").read_bytes() != before
