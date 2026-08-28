"""Read-only modeling doctor."""

from __future__ import annotations

import platform
import sys

from .constants import CONTRACT_VERSION
from .engines import (
    binomial_square,
    effective_energy,
    euler_exponential,
    euler_soc,
    mean_and_sample_variance,
    ordinary_least_squares,
    quadratic_grid_minimum,
    relative_sensitivity,
    shortest_path_length,
    solve_two_var_lp,
    time_to_empty,
    time_to_empty_piecewise,
    total_power,
    tte_component_elasticity,
)


def doctor_text() -> tuple[str, int]:
    length = shortest_path_length([("A", "B"), ("B", "C")], "A", "C")
    x, value = quadratic_grid_minimum(0.0, 1.0, 20)
    direct, expanded = binomial_square(3.0, 4.0)
    approx, exact = euler_exponential(40, 1.0)
    intercept, slope = ordinary_least_squares([0.0, 1.0, 2.0], [1.0, 3.0, 5.0])
    elasticity = relative_sensitivity(lambda x: x * x, 2.0)
    mean, variance = mean_and_sample_variance([1.0, 2.0, 3.0])
    lp_x, lp_y, lp_obj = solve_two_var_lp((1.0, 1.0), [(1.0, 2.0, 4.0), (2.0, 1.0, 4.0)])
    soc_power = total_power(0.3, 1.5, 0.8, 0.2, 0.1, 0.1)
    soc_tte = time_to_empty(1.0, soc_power, effective_energy(15.0, 1.0, 1.0))
    soc_approx = euler_soc(steps=200, t_end=2.5, soc0=1.0, power=soc_power, e_eff=15.0)
    elas_screen = tte_component_elasticity((0.3, 1.5, 0.8, 0.2, 0.1, 0.1), 1)
    tte_burst = time_to_empty_piecewise(1.0, ((6.0, 1.0), (0.3, 100.0)), 15.0)
    tte_idle_first = time_to_empty_piecewise(1.0, ((0.3, 1.0), (6.0, 100.0)), 15.0)
    ok = (
        length == 2
        and abs(x) < 1e-12
        and abs(value) < 1e-12
        and abs(direct - expanded) < 1e-12
        and abs(approx - exact) <= 0.05
        and abs(intercept - 1.0) < 1e-12
        and abs(slope - 2.0) < 1e-12
        and abs(elasticity - 2.0) < 1e-4
        and abs(mean - 2.0) < 1e-12
        and abs(variance - 1.0) < 1e-12
        and abs(lp_obj - 8.0 / 3.0) < 1e-9
        and abs(soc_tte - 5.0) < 1e-12
        and abs(soc_approx - 0.5) <= 1e-6
        and abs(elas_screen + 0.5) < 1e-12
        and abs(tte_burst - 31.0) < 1e-12
        and abs(tte_idle_first - 3.45) < 1e-12
    )
    lines = [
        f"Modeling Contract {CONTRACT_VERSION}",
        f"python: {sys.version.split()[0]}",
        f"os: {platform.system()}",
        "engines: network, quadratic, symbolic, ode, ols, sensitivity, stats, lp, soc, soc_sensitivity, soc_piecewise (stdlib)",
        "root requirements: no solver Sidecar installed",
        f"known_answer_network: {length}",
        f"known_answer_quadratic: x={x} value={value}",
        f"known_answer_symbolic: {direct} vs {expanded}",
        f"known_answer_ode: {approx} vs {exact}",
        f"known_answer_ols: intercept={intercept} slope={slope}",
        f"known_answer_sensitivity: {elasticity}",
        f"known_answer_stats: mean={mean} var={variance}",
        f"known_answer_lp: x={lp_x} y={lp_y} obj={lp_obj}",
        f"known_answer_soc: tte={soc_tte} euler={soc_approx} elas_screen={elas_screen} burst={tte_burst} idle_first={tte_idle_first}",
        "families_claimed: 9 PILOT; not 15; soc_sensitivity/soc_piecewise are the same energy-balance family",
        "doctor: PASS" if ok else "doctor: FAIL",
    ]
    return "\n".join(lines) + "\n", 0 if ok else 1
