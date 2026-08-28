from pathlib import Path

from tools.workbench.experiment import run_contest_experiment


def test_run_experiment_writes_under_code_outputs(tmp_path: Path):
    name = "美赛2026-A"
    (tmp_path / "07_项目" / name).mkdir(parents=True)
    (tmp_path / "05_代码" / name / "outputs").mkdir(parents=True)
    result = run_contest_experiment(
        name=name,
        engine="soc",
        run_id="soc-exp-1",
        repo_root=tmp_path,
    )
    assert result.status == "SUCCEEDED"
    assert (tmp_path / "05_代码" / name / "outputs" / "soc-exp-1" / "metrics.json").is_file()


def test_run_experiment_rejects_missing_scaffold(tmp_path: Path):
    result = run_contest_experiment(
        name="missing",
        engine="soc",
        run_id="x",
        repo_root=tmp_path,
    )
    assert result.status == "REJECTED"
