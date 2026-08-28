from tools.research_project.constants import REQUIRED_DIRS, REQUIRED_FILES
from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import init_project


def test_init_creates_required_scaffold(tmp_repo):
    project = tmp_repo / "07_项目" / "New_Project"
    result = init_project(project, title="New Project", repo_root=tmp_repo)
    assert result.kind == ResearchProjectOperationKind.WRITTEN
    for name in REQUIRED_FILES:
        assert (project / name).is_file()
    for name in REQUIRED_DIRS:
        assert (project / name).is_dir()


def test_init_complete_is_noop(tmp_repo):
    project = tmp_repo / "07_项目" / "Existing"
    assert init_project(project, title="Existing", repo_root=tmp_repo).kind == ResearchProjectOperationKind.WRITTEN
    before = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    result = init_project(project, title="Existing", repo_root=tmp_repo)
    assert result.kind == ResearchProjectOperationKind.NO_OP
    after = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    assert before == after


def test_init_incomplete_is_rejected_with_zero_change(tmp_repo):
    project = tmp_repo / "07_项目" / "Broken"
    project.mkdir(parents=True)
    (project / "assumptions.md").write_text("partial\n", encoding="utf-8", newline="\n")
    before = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    result = init_project(project, title="Broken", repo_root=tmp_repo)
    assert result.kind == ResearchProjectOperationKind.REJECTED
    after = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
    assert before == after


def test_init_rejects_template_and_escape_and_knowledge(tmp_repo):
    assert init_project(tmp_repo / "07_项目" / "_模板" / "x", "x", repo_root=tmp_repo).kind == ResearchProjectOperationKind.REJECTED
    assert init_project(tmp_repo / "07_项目" / ".." / "01_知识库" / "evil", "x", repo_root=tmp_repo).kind == ResearchProjectOperationKind.REJECTED


def test_init_path_with_spaces(tmp_repo):
    project = tmp_repo / "07_项目" / "My Project Name"
    assert init_project(project, "My Project Name", repo_root=tmp_repo).kind == ResearchProjectOperationKind.WRITTEN
