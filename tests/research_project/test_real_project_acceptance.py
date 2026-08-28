import hashlib
from pathlib import Path

from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import (
    add_assumption,
    add_claim,
    add_evidence,
    append_decision,
    init_project,
    reconcile_project,
    record_negative_result,
    supersede_assumption,
    update_governance,
)
from tools.research_project.parser import parse_project
from tools.research_project.stale import dossier_is_stale
from tools.research_project.validator import validate_project


def _sha256_tree(root: Path) -> dict[str, str]:
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            out[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def test_disposable_acceptance_pipeline(tmp_path):
    candidates = Path("tests/research_project/fixtures/disposable_project")
    repo = tmp_path / "repo"
    knowledge = repo / "01_知识库"
    attempts = repo / "11_学习证据"
    knowledge.mkdir(parents=True)
    attempts.mkdir(parents=True)
    (knowledge / "KEEP.md").write_text("unchanged\n", encoding="utf-8", newline="\n")
    (attempts / "KEEP.md").write_text("unchanged\n", encoding="utf-8", newline="\n")
    before_k = _sha256_tree(knowledge)
    before_a = _sha256_tree(attempts)

    project = repo / "07_项目" / "Disposable_RP"
    assert init_project(project, "Disposable", repo_root=repo).kind == ResearchProjectOperationKind.WRITTEN
    assert add_assumption(project, candidates / "asm_0001.md").kind == ResearchProjectOperationKind.WRITTEN
    assert supersede_assumption(project, "ASM-0001", candidates / "asm_0002.md").kind == ResearchProjectOperationKind.WRITTEN
    assert add_claim(project, candidates / "clm_0001_no_refs.md").kind == ResearchProjectOperationKind.WRITTEN
    assert add_evidence(project, candidates / "evd_0001.md").kind == ResearchProjectOperationKind.WRITTEN
    docs = parse_project(project)
    assert docs.claims[0].evidence_refs == ["EVD-0001"]
    assert docs.evidence[0].claim_ref == "CLM-0001"
    assert docs.claims[0].status == "OPEN"
    assert append_decision(project, candidates / "dec_0001.md").kind == ResearchProjectOperationKind.WRITTEN
    assert record_negative_result(project, candidates / "neg_0001.md").kind == ResearchProjectOperationKind.WRITTEN
    assert update_governance(project, candidates / "aic_0001.md").kind == ResearchProjectOperationKind.WRITTEN
    r1 = reconcile_project(project)
    assert r1.kind == ResearchProjectOperationKind.WRITTEN
    assert dossier_is_stale(project) is False
    r2 = reconcile_project(project)
    assert r2.kind == ResearchProjectOperationKind.NO_OP
    assert validate_project(project).ok is True
    assert _sha256_tree(knowledge) == before_k
    assert _sha256_tree(attempts) == before_a
