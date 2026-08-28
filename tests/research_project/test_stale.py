from tools.research_project.constants import DOSSIER_BEGIN
from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import add_assumption, add_claim, reconcile_project
from tools.research_project.stale import dossier_is_stale


def test_fresh_scaffold_not_stale(tmp_project):
    reconcile_project(tmp_project)
    assert dossier_is_stale(tmp_project) is False


def test_canonical_mutation_then_reconcile_idempotent(tmp_project, candidate_asm):
    assert dossier_is_stale(tmp_project) is False
    add_assumption(tmp_project, candidate_asm)
    assert dossier_is_stale(tmp_project) is True
    human_before = (tmp_project / "research_dossier.md").read_text(encoding="utf-8").split(DOSSIER_BEGIN)[0]
    r1 = reconcile_project(tmp_project)
    assert r1.kind == ResearchProjectOperationKind.WRITTEN
    assert dossier_is_stale(tmp_project) is False
    r2 = reconcile_project(tmp_project)
    assert r2.kind == ResearchProjectOperationKind.NO_OP
    human_after = (tmp_project / "research_dossier.md").read_text(encoding="utf-8").split(DOSSIER_BEGIN)[0]
    assert human_before == human_after
    gen = (tmp_project / "research_dossier.md").read_text(encoding="utf-8")
    assert "RECONCILE_REQUIRED" not in gen


def test_reconcile_rejects_damaged_markers(tmp_project):
    p = tmp_project / "research_dossier.md"
    p.write_text("# Dossier\n<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED BEGIN -->\n", encoding="utf-8", newline="\n")
    before = p.read_bytes()
    result = reconcile_project(tmp_project)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert p.read_bytes() == before


def test_next_steps_only_deterministic_rules(tmp_project, candidate_clm_no_refs):
    add_claim(tmp_project, candidate_clm_no_refs)
    reconcile_project(tmp_project)
    gen = (tmp_project / "research_dossier.md").read_text(encoding="utf-8")
    assert "CLM-0001" in gen
    assert "research direction" not in gen.lower()
