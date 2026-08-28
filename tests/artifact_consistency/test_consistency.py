from pathlib import Path

from tools.artifact_consistency.checks import (
    check_ai_contribution,
    check_citations,
    check_knowledge_promotion,
    check_latex_figures,
    check_lean_refs,
    check_p9_publish_boundary,
)


def test_unprovenanced_includegraphics_fails(tmp_path: Path):
    tex = tmp_path / "paper.tex"
    tex.write_text(r"\includegraphics{plot.png}" + "\n", encoding="utf-8")
    result = check_latex_figures(tmp_path, tmp_path / "artifacts")
    assert result.ok is False


def test_manifested_figure_passes(tmp_path: Path):
    tex = tmp_path / "paper.tex"
    tex.write_text(r"\includegraphics{fig-num-001}" + "\n", encoding="utf-8")
    manifest = tmp_path / "artifacts" / "fig-num-001" / "manifest.yaml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("figure_id: fig-num-001\n", encoding="utf-8")
    assert check_latex_figures(tmp_path, tmp_path / "artifacts").ok is True


def test_knowledge_requires_authorization(tmp_path: Path):
    knowledge = tmp_path / "01_知识库"
    knowledge.mkdir()
    (knowledge / "K0001.md").write_text("id: K0001\n", encoding="utf-8")
    blocked = check_knowledge_promotion(knowledge, authorized=False)
    allowed = check_knowledge_promotion(knowledge, authorized=True)
    assert blocked.ok is False
    assert allowed.ok is True


def test_direct_formal_pdf_write_blocked(tmp_path: Path):
    formal = tmp_path / "08_成果输出" / "PDF"
    formal.mkdir(parents=True)
    target = formal / "topic.pdf"
    assert check_p9_publish_boundary(target, formal).ok is False
    isolated = tmp_path / "build" / "topic.pdf"
    isolated.parent.mkdir()
    assert check_p9_publish_boundary(isolated, formal).ok is True


def test_unknown_citation_and_leanref_fail():
    assert check_citations(r"\cite{missing}", {"lit1"}).ok is False
    assert check_citations(r"\cite{lit1}", {"lit1"}).ok is True
    assert check_lean_refs(r"\leanref{ALG-001}", {"ALG-001"}).ok is True
    assert check_lean_refs(r"\leanref{NOPE}", {"ALG-001"}).ok is False


def test_ai_contribution_must_be_recorded():
    paper = "This draft was AI generated."
    assert check_ai_contribution(paper, "GOVERNANCE only").ok is False
    assert check_ai_contribution(paper, "AI_CONTRIBUTION recorded").ok is True
