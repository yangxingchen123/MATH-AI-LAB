from pathlib import Path

from tools.modeling.engines import mean_and_sample_variance, solve_two_var_lp
from tools.modeling.runner import run_lp_pilot, run_stats_pilot


def test_sample_stats_known_triple():
    mean, variance = mean_and_sample_variance([1.0, 2.0, 3.0])
    assert abs(mean - 2.0) < 1e-12
    assert abs(variance - 1.0) < 1e-12


def test_two_var_lp_known_vertex():
    x, y, objective = solve_two_var_lp(
        (1.0, 1.0),
        [(1.0, 2.0, 4.0), (2.0, 1.0, 4.0)],
    )
    assert abs(x - 4.0 / 3.0) < 1e-9
    assert abs(y - 4.0 / 3.0) < 1e-9
    assert abs(objective - 8.0 / 3.0) < 1e-9


def test_stats_and_lp_pilots(tmp_path: Path):
    assert run_stats_pilot(tmp_path, "stats-1").status == "SUCCEEDED"
    assert run_lp_pilot(tmp_path, "lp-1").status == "SUCCEEDED"
