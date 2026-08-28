from pathlib import Path

from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import init_project


def test_init_contest_kind_adds_modeling_files(tmp_repo):
    project = tmp_repo / "07_项目" / "MCM_A"
    result = init_project(
        project,
        "Contest",
        repo_root=tmp_repo,
        kind="contest_modeling",
    )
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    assert (project / "model_selection.md").is_file()
    assert (project / "problem.md").is_file()
    text = (project / "research_dossier.md").read_text(encoding="utf-8")
    assert "数学建模竞赛" in text
    assert "MATH-AI-LAB:RESEARCH-DOSSIER GENERATED BEGIN" in text


def test_init_literature_kind_adds_reading_notes(tmp_repo):
    project = tmp_repo / "07_项目" / "Paper_Read"
    result = init_project(
        project,
        "Paper",
        repo_root=tmp_repo,
        kind="literature",
    )
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    assert (project / "reading_notes.md").is_file()
    assert (project / "source_map.md").is_file()


def test_init_rejects_unknown_kind(tmp_repo):
    project = tmp_repo / "07_项目" / "Bad"
    result = init_project(project, "Bad", repo_root=tmp_repo, kind="thesis")
    assert result.kind == ResearchProjectOperationKind.REJECTED
    assert not project.exists()
