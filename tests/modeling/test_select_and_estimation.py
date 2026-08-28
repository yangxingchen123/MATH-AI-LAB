from pathlib import Path

from tools.modeling.engines import ordinary_least_squares, relative_sensitivity
from tools.modeling.runner import run_ols_pilot, run_sensitivity_pilot
from tools.modeling.select import rank_model_candidates


def test_ols_recovers_known_line():
    intercept, slope = ordinary_least_squares([0.0, 1.0, 2.0], [1.0, 3.0, 5.0])
    assert abs(intercept - 1.0) < 1e-12
    assert abs(slope - 2.0) < 1e-12


def test_relative_sensitivity_of_square():
    value = relative_sensitivity(lambda x: x * x, 2.0)
    assert abs(value - 2.0) < 1e-4


def test_rank_rejects_incomplete_candidate():
    ranked = rank_model_candidates(
        [
            {
                "name": "logistic",
                "target_question": "growth",
                "why": "bounded carrying capacity",
                "data_requirement": "time series of population",
                "identifiable_when": "at least two distinct times",
                "falsifiable_when": "population exceeds carrying capacity",
            },
            {"name": "vague"},
        ]
    )
    assert ranked[0]["name"] == "logistic"
    assert ranked[0]["eligible"] is True
    assert ranked[1]["eligible"] is False
    assert "why" in ranked[1]["missing"]


def test_select_cli_allows_explicit_rejects(tmp_path: Path):
    from tools.modeling.cli import main

    path = tmp_path / "candidates.yaml"
    path.write_text(
        "candidates:\n"
        "  - name: keep\n"
        "    target_question: q\n"
        "    why: because\n"
        "    data_requirement: none\n"
        "    identifiable_when: always\n"
        "    falsifiable_when: never\n"
        "  - name: drop\n"
        "    target_question: q\n"
        "    why: because\n"
        "    data_requirement: none\n"
        "    identifiable_when: always\n"
        "    falsifiable_when: never\n"
        "    rejected: true\n",
        encoding="utf-8",
        newline="\n",
    )
    assert main(["select", "--path", str(path)]) == 0


def test_ols_and_sensitivity_pilots(tmp_path: Path):
    ols = run_ols_pilot(tmp_path, "ols-1")
    sens = run_sensitivity_pilot(tmp_path, "sens-1")
    assert ols.status == "SUCCEEDED"
    assert sens.status == "SUCCEEDED"
