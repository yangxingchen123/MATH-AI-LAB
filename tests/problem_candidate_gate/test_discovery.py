from pathlib import Path

from tools.problem_candidate_gate.discovery import discover_markdown_files, is_template_file
from tools.problem_candidate_gate.readiness import check_project

from .conftest import problem_md


def test_discovers_problem_dir(project: Path) -> None:
    path = project / "02_题目库" / "已解决" / "a.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(problem_md(), encoding="utf-8")
    included, excluded = discover_markdown_files(project)
    assert any(p.resolve() == path.resolve() for p in included)
    assert any(is_template_file(p, project) for p in excluded)


def test_recursive_md(project: Path) -> None:
    nested = project / "02_题目库" / "研究中" / "deep" / "x.md"
    nested.parent.mkdir(parents=True, exist_ok=True)
    nested.write_text(problem_md(pid="P0002"), encoding="utf-8")
    included, _ = discover_markdown_files(project)
    assert nested.resolve() in included


def test_template_excluded_by_path(project: Path) -> None:
    included, excluded = discover_markdown_files(project)
    template = (project / "02_题目库" / "题目模板.md").resolve()
    assert template in excluded
    assert template not in included


def test_stable_sort(project: Path) -> None:
    (project / "02_题目库" / "b.md").write_text(problem_md(pid="P0002"), encoding="utf-8")
    (project / "02_题目库" / "a.md").write_text(problem_md(pid="P0001"), encoding="utf-8")
    included, _ = discover_markdown_files(project)
    rels = [p.name for p in included]
    assert rels == sorted(rels)


def test_no_yaml_warning_not_error(project: Path) -> None:
    (project / "02_题目库" / "note.md").write_text("# just a note\n", encoding="utf-8")
    r = check_project(root=project)
    assert r.summary.errors == 0
    assert any(i.rule_id == "PCG-DISC-W001" for i in r.issues)
