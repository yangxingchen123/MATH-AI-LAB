from pathlib import Path

from tools.modeling.engines import (
    effective_energy,
    euler_soc,
    euler_soc_piecewise,
    relative_sensitivity,
    soc_constant_power,
    soc_piecewise,
    time_to_empty,
    time_to_empty_piecewise,
    total_power,
    tte_component_elasticity,
)
from tools.modeling.runner import (
    run_soc_pilot,
    run_soc_piecewise_pilot,
    run_soc_sensitivity_pilot,
)


def test_constant_power_tte_is_energy_over_power():
    e_eff = effective_energy(15.0, 1.0, 1.0)
    power = total_power(0.3, 1.5, 0.8, 0.2, 0.1, 0.1)
    assert abs(power - 3.0) < 1e-12
    tte = time_to_empty(1.0, power, e_eff)
    assert abs(tte - 5.0) < 1e-12
    assert abs(soc_constant_power(2.5, 1.0, power, e_eff) - 0.5) < 1e-12


def test_euler_matches_analytical_soc():
    power = 3.0
    e_eff = 15.0
    approx = euler_soc(steps=200, t_end=2.5, soc0=1.0, power=power, e_eff=e_eff)
    exact = soc_constant_power(2.5, 1.0, power, e_eff)
    assert abs(approx - exact) <= 1e-6


def test_soc_pilot_known_answer(tmp_path: Path):
    result = run_soc_pilot(tmp_path, "soc-1")
    assert result.status == "SUCCEEDED"
    assert abs(result.metrics["tte_hours"] - 5.0) <= 1e-9
    assert (tmp_path / "soc-1" / "manifest.yaml").is_file()


def test_component_elasticity_is_negative_power_share():
    parts = (0.3, 1.5, 0.8, 0.2, 0.1, 0.1)
    assert abs(sum(parts) - 3.0) < 1e-12
    assert abs(tte_component_elasticity(parts, 1) + 1.5 / 3.0) < 1e-12
    elas_p = relative_sensitivity(lambda power: time_to_empty(1.0, power, 15.0), 3.0)
    assert abs(elas_p + 1.0) < 1e-4


def test_piecewise_order_changes_tte():
    e_eff = 15.0
    burst_first = ((6.0, 1.0), (0.3, 100.0))
    idle_first = ((0.3, 1.0), (6.0, 100.0))
    assert abs(time_to_empty_piecewise(1.0, burst_first, e_eff) - 31.0) < 1e-12
    assert abs(time_to_empty_piecewise(1.0, idle_first, e_eff) - 3.45) < 1e-12
    assert abs(soc_piecewise(1.0, 1.0, burst_first, e_eff) - 0.6) < 1e-12
    approx = euler_soc_piecewise(
        steps=200, t_end=1.0, soc0=1.0, segments=burst_first, e_eff=e_eff
    )
    assert abs(approx - 0.6) <= 1e-6


def test_soc_sensitivity_pilot_known_answer(tmp_path: Path):
    result = run_soc_sensitivity_pilot(tmp_path, "soc-sens-1")
    assert result.status == "SUCCEEDED"
    assert abs(result.metrics["elas_total_power"] + 1.0) <= 1e-4
    assert abs(result.metrics["elas_screen"] + 0.5) <= 1e-9
    assert abs(result.metrics["tte_cold_hours"] - 3.75) <= 1e-9


def test_soc_piecewise_pilot_known_answer(tmp_path: Path):
    result = run_soc_piecewise_pilot(tmp_path, "soc-pw-1")
    assert result.status == "SUCCEEDED"
    assert abs(result.metrics["tte_burst_first_hours"] - 31.0) <= 1e-9
    assert abs(result.metrics["tte_idle_first_hours"] - 3.45) <= 1e-9
