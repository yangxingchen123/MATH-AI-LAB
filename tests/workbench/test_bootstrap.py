from pathlib import Path

from tools.workbench.bootstrap import bootstrap_contest


def test_bootstrap_contest_creates_three_roots(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "07_项目").mkdir(parents=True)
    result = bootstrap_contest(name="MCM_A", title="Contest A", repo_root=repo)
    assert result.status == "WRITTEN"
    project = repo / "07_项目" / "MCM_A"
    code = repo / "05_代码" / "MCM_A"
    tex_dir = repo / "04_LATEX" / "数学建模" / "MCM_A"
    assert (project / "model_selection.md").is_file()
    assert (code / "README.md").is_file()
    assert (tex_dir / "MCM_A.tex").is_file()
    plan = (project / "experiment_plan.md").read_text(encoding="utf-8")
    assert "05_代码/MCM_A" in plan
    assert "04_LATEX/数学建模/MCM_A" in plan


def test_bootstrap_contest_is_noop_when_complete(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "07_项目").mkdir(parents=True)
    first = bootstrap_contest(name="MCM_A", title="Contest A", repo_root=repo)
    second = bootstrap_contest(name="MCM_A", title="Contest A", repo_root=repo)
    assert first.status == "WRITTEN"
    assert second.status == "NO_OP"


def test_bootstrap_rejects_escape(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "07_项目").mkdir(parents=True)
    result = bootstrap_contest(name="..", title="x", repo_root=repo)
    assert result.status == "REJECTED"
