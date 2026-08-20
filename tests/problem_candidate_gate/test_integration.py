from pathlib import Path

from tools.problem_candidate_gate.readiness import check_file, check_project, status_project

from .conftest import knowledge_md, problem_md


def test_source_files_unmodified(project: Path) -> None:
    path = project / "02_题目库" / "a.md"
    original = problem_md(extras="parts:\n  - a\n  - b")
    path.write_text(original, encoding="utf-8")
    kpath = project / "01_知识库" / "K0001.md"
    kbody = knowledge_md(kid="K0001")
    kpath.write_text(kbody, encoding="utf-8")
    before_p = path.read_bytes()
    before_k = kpath.read_bytes()
    check_project(root=project)
    status_project(root=project)
    check_file(path, root=project)
    assert path.read_bytes() == before_p
    assert kpath.read_bytes() == before_k


def test_template_not_treated_as_candidate(project: Path) -> None:
    r = check_project(root=project)
    files = [d.relative_path for d in r.documents]
    assert not any("题目模板.md" in f for f in files)


def test_p0000_not_skipped_as_template(project: Path) -> None:
    (project / "02_题目库" / "sentinel.md").write_text(
        problem_md(pid="P0000"), encoding="utf-8"
    )
    r = check_project(root=project)
    assert any(i.rule_id == "PCG-BASE-011" for i in r.issues)
