from pathlib import Path

from tools.modeling.contest_sidecar import (
    CONTEST_REQUIREMENTS,
    CONTEST_ML_REQUIREMENTS,
    INTEGRATED_AHP_TEMPLATE,
    doctor,
    smoke_ahp,
)
from tools.research_project.constants import REPO_ROOT


def test_contest_sidecar_requirements_are_not_root():
    root_req = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "numpy" not in root_req
    assert "matplotlib" not in root_req
    assert "scipy" not in root_req
    assert CONTEST_REQUIREMENTS.is_file()
    assert CONTEST_ML_REQUIREMENTS.is_file()
    sidecar = CONTEST_REQUIREMENTS.read_text(encoding="utf-8").lower()
    assert "numpy" in sidecar
    assert "matplotlib" in sidecar


def test_upstream_skills_are_copied_into_project_trees():
    solver_ref = (
        REPO_ROOT
        / ".cursor"
        / "skills"
        / "math-modeling-solver"
        / "references"
        / "problem-decomposition.md"
    )
    paper_ref = (
        REPO_ROOT
        / ".cursor"
        / "skills"
        / "math-modeling-paper"
        / "references"
        / "cumcm-guide.md"
    )
    assert solver_ref.is_file()
    assert paper_ref.is_file()
    assert INTEGRATED_AHP_TEMPLATE.is_file()
    solver_skill = (
        REPO_ROOT / ".cursor" / "skills" / "math-modeling-solver" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "MATH-AI-LAB" in solver_skill
    assert "02_题目库" in solver_skill


def test_contest_sidecar_doctor_never_blocks_core():
    report = doctor()
    assert report["core_impact"] is False
    assert report["vendor"] == "PASS"
    assert report["cursor_skills"] == "PASS"
    assert report["status"] in {"PASS", "DEGRADED"}
    assert report["install"].endswith("tools/modeling/requirements-contest.txt")


def test_contest_sidecar_cli_is_degraded_ok_without_numpy():
    from tools.modeling.cli import main

    assert main(["contest-doctor"]) == 0
    assert main(["contest-smoke"]) == 0


def test_ahp_smoke_when_numpy_present():
    outcome = smoke_ahp()
    if outcome["status"] == "SKIPPED":
        assert "numpy" in outcome["message"].lower()
        return
    assert outcome["status"] == "SUCCEEDED"
    assert abs(outcome["weight_sum"] - 1.0) < 1e-9
    assert outcome["cr"] < 0.1
