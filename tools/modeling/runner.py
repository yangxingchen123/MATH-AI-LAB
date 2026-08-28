"""Execute stdlib modeling pilots into immutable run directories."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

from .engines import (
    binomial_square,
    effective_energy,
    euler_exponential,
    euler_soc,
    euler_soc_piecewise,
    mean_and_sample_variance,
    ordinary_least_squares,
    quadratic_grid_minimum,
    relative_sensitivity,
    shortest_path_length,
    soc_constant_power,
    soc_piecewise,
    solve_two_var_lp,
    time_to_empty,
    time_to_empty_piecewise,
    total_power,
    tte_component_elasticity,
)
from .manifest import sha256_bytes, validate_manifest
from .models import RunResult

NETWORK_FIXTURE = {
    "edges": [["A", "B"], ["B", "C"]],
    "source": "A",
    "target": "C",
    "expected_length": 2,
}

QUAD_FIXTURE = {
    "lo": 0.0,
    "hi": 1.0,
    "steps": 20,
    "expected_x": 0.0,
    "expected_value": 0.0,
    "tolerance": 1e-12,
}

SYMBOLIC_FIXTURE = {"a": 3.0, "b": 4.0}

ODE_FIXTURE = {"steps": 40, "t": 1.0, "tolerance": 0.05}

OLS_FIXTURE = {
    "xs": [0.0, 1.0, 2.0],
    "ys": [1.0, 3.0, 5.0],
    "expected_intercept": 1.0,
    "expected_slope": 2.0,
    "tolerance": 1e-12,
}

SENS_FIXTURE = {"x": 2.0, "expected": 2.0, "tolerance": 1e-4}

STATS_FIXTURE = {
    "xs": [1.0, 2.0, 3.0],
    "expected_mean": 2.0,
    "expected_variance": 1.0,
    "tolerance": 1e-12,
}

LP_FIXTURE = {
    "objective": [1.0, 1.0],
    "constraints": [[1.0, 2.0, 4.0], [2.0, 1.0, 4.0]],
    "expected": [4.0 / 3.0, 4.0 / 3.0, 8.0 / 3.0],
    "tolerance": 1e-9,
}

SOC_PIECEWISE_FIXTURE = {
    "e_nom": 15.0,
    "soc0": 1.0,
    "burst_first": [[6.0, 1.0], [0.3, 100.0]],
    "idle_first": [[0.3, 1.0], [6.0, 100.0]],
    "expected_burst": 31.0,
    "expected_idle": 3.45,
    "euler_t": 1.0,
    "expected_soc": 0.6,
    "tolerance": 1e-6,
}

SOC_SENS_FIXTURE = {
    "e_nom": 15.0,
    "parts": [0.3, 1.5, 0.8, 0.2, 0.1, 0.1],
    "soc0": 1.0,
    "eta_cold": 0.75,
    "age": 0.85,
    "expected_tte": 5.0,
    "expected_elas_screen": -0.5,
    "expected_tte_cold": 3.75,
    "tolerance": 1e-6,
}

SOC_FIXTURE = {
    "e_nom": 15.0,
    "eta_temp": 1.0,
    "age": 1.0,
    "idle": 0.3,
    "screen": 1.5,
    "cpu": 0.8,
    "net": 0.2,
    "gps": 0.1,
    "background": 0.1,
    "soc0": 1.0,
    "expected_power": 3.0,
    "expected_tte": 5.0,
    "euler_steps": 200,
    "euler_t": 2.5,
    "expected_soc": 0.5,
    "tolerance": 1e-6,
}


def _new_run_dir(root: Path, run_id: str) -> Path:
    dest = Path(root) / run_id
    if dest.exists():
        raise FileExistsError(f"run_id already exists: {run_id}")
    dest.mkdir(parents=True)
    return dest


def run_network_pilot(output_root: Path, run_id: str = "net-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    length = shortest_path_length(
        [(a, b) for a, b in NETWORK_FIXTURE["edges"]],
        NETWORK_FIXTURE["source"],
        NETWORK_FIXTURE["target"],
    )
    expected = NETWORK_FIXTURE["expected_length"]
    status = "SUCCEEDED" if length == expected else "FAILED"
    metrics = {"path_length": float(length), "expected": float(expected)}
    return _finalize(dest, run_id, status, metrics, "network_shortest_path", NETWORK_FIXTURE)


def run_quadratic_pilot(output_root: Path, run_id: str = "opt-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    x, value = quadratic_grid_minimum(
        QUAD_FIXTURE["lo"], QUAD_FIXTURE["hi"], QUAD_FIXTURE["steps"]
    )
    ok = abs(x - QUAD_FIXTURE["expected_x"]) <= QUAD_FIXTURE["tolerance"] and abs(
        value - QUAD_FIXTURE["expected_value"]
    ) <= QUAD_FIXTURE["tolerance"]
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {"x": x, "value": value}
    return _finalize(dest, run_id, status, metrics, "quadratic_grid_min", QUAD_FIXTURE)


def run_symbolic_pilot(output_root: Path, run_id: str = "sym-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    direct, expanded = binomial_square(SYMBOLIC_FIXTURE["a"], SYMBOLIC_FIXTURE["b"])
    status = "SUCCEEDED" if abs(direct - expanded) < 1e-12 else "FAILED"
    metrics = {"direct": direct, "expanded": expanded}
    return _finalize(dest, run_id, status, metrics, "binomial_square", SYMBOLIC_FIXTURE)


def run_ode_pilot(output_root: Path, run_id: str = "ode-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    approx, exact = euler_exponential(ODE_FIXTURE["steps"], ODE_FIXTURE["t"])
    ok = abs(approx - exact) <= ODE_FIXTURE["tolerance"]
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {"approx": approx, "exact": exact, "error": abs(approx - exact)}
    return _finalize(dest, run_id, status, metrics, "euler_exponential", ODE_FIXTURE)


def run_ols_pilot(output_root: Path, run_id: str = "ols-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    intercept, slope = ordinary_least_squares(OLS_FIXTURE["xs"], OLS_FIXTURE["ys"])
    ok = (
        abs(intercept - OLS_FIXTURE["expected_intercept"]) <= OLS_FIXTURE["tolerance"]
        and abs(slope - OLS_FIXTURE["expected_slope"]) <= OLS_FIXTURE["tolerance"]
    )
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {"intercept": intercept, "slope": slope}
    return _finalize(dest, run_id, status, metrics, "ordinary_least_squares", OLS_FIXTURE)


def run_sensitivity_pilot(output_root: Path, run_id: str = "sens-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    value = relative_sensitivity(lambda x: x * x, SENS_FIXTURE["x"])
    ok = abs(value - SENS_FIXTURE["expected"]) <= SENS_FIXTURE["tolerance"]
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {"elasticity": value, "expected": SENS_FIXTURE["expected"]}
    return _finalize(dest, run_id, status, metrics, "relative_sensitivity", SENS_FIXTURE)


def run_stats_pilot(output_root: Path, run_id: str = "stats-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    mean, variance = mean_and_sample_variance(STATS_FIXTURE["xs"])
    ok = (
        abs(mean - STATS_FIXTURE["expected_mean"]) <= STATS_FIXTURE["tolerance"]
        and abs(variance - STATS_FIXTURE["expected_variance"]) <= STATS_FIXTURE["tolerance"]
    )
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {"mean": mean, "variance": variance}
    return _finalize(dest, run_id, status, metrics, "sample_stats", STATS_FIXTURE)


def run_soc_pilot(output_root: Path, run_id: str = "soc-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    e_eff = effective_energy(
        SOC_FIXTURE["e_nom"], SOC_FIXTURE["eta_temp"], SOC_FIXTURE["age"]
    )
    power = total_power(
        SOC_FIXTURE["idle"],
        SOC_FIXTURE["screen"],
        SOC_FIXTURE["cpu"],
        SOC_FIXTURE["net"],
        SOC_FIXTURE["gps"],
        SOC_FIXTURE["background"],
    )
    tte = time_to_empty(SOC_FIXTURE["soc0"], power, e_eff)
    approx = euler_soc(
        steps=SOC_FIXTURE["euler_steps"],
        t_end=SOC_FIXTURE["euler_t"],
        soc0=SOC_FIXTURE["soc0"],
        power=power,
        e_eff=e_eff,
    )
    exact = soc_constant_power(
        SOC_FIXTURE["euler_t"], SOC_FIXTURE["soc0"], power, e_eff
    )
    idle_tte = time_to_empty(SOC_FIXTURE["soc0"], SOC_FIXTURE["idle"], e_eff)
    ok = (
        abs(power - SOC_FIXTURE["expected_power"]) <= SOC_FIXTURE["tolerance"]
        and abs(tte - SOC_FIXTURE["expected_tte"]) <= SOC_FIXTURE["tolerance"]
        and abs(approx - exact) <= SOC_FIXTURE["tolerance"]
        and abs(exact - SOC_FIXTURE["expected_soc"]) <= SOC_FIXTURE["tolerance"]
    )
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {
        "power_w": power,
        "tte_hours": tte,
        "soc_euler": approx,
        "soc_exact": exact,
        "tte_idle_hours": idle_tte,
    }
    return _finalize(dest, run_id, status, metrics, "energy_balance_soc", SOC_FIXTURE)


def run_soc_sensitivity_pilot(
    output_root: Path, run_id: str = "soc-sens-pilot-001"
) -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    parts = tuple(SOC_SENS_FIXTURE["parts"])
    e_nom = SOC_SENS_FIXTURE["e_nom"]
    soc0 = SOC_SENS_FIXTURE["soc0"]
    power = total_power(*parts)
    e_eff = effective_energy(e_nom, 1.0, 1.0)
    tte = time_to_empty(soc0, power, e_eff)
    tte_idle = time_to_empty(soc0, parts[0], e_eff)
    tte_cold = time_to_empty(
        soc0, power, effective_energy(e_nom, SOC_SENS_FIXTURE["eta_cold"], 1.0)
    )
    tte_aged = time_to_empty(
        soc0, power, effective_energy(e_nom, 1.0, SOC_SENS_FIXTURE["age"])
    )
    elas_power = relative_sensitivity(lambda value: time_to_empty(soc0, value, e_eff), power)
    elas_energy = relative_sensitivity(
        lambda value: time_to_empty(soc0, power, value), e_eff
    )
    names = ("idle", "screen", "cpu", "net", "gps", "bg")
    elas = {name: tte_component_elasticity(parts, index) for index, name in enumerate(names)}
    screen_up = list(parts)
    screen_up[1] *= 1.2
    tte_screen_plus20 = time_to_empty(soc0, total_power(*screen_up), e_eff)
    ok = (
        abs(tte - SOC_SENS_FIXTURE["expected_tte"]) <= SOC_SENS_FIXTURE["tolerance"]
        and abs(elas["screen"] - SOC_SENS_FIXTURE["expected_elas_screen"])
        <= SOC_SENS_FIXTURE["tolerance"]
        and abs(tte_cold - SOC_SENS_FIXTURE["expected_tte_cold"])
        <= SOC_SENS_FIXTURE["tolerance"]
        and abs(elas_power + 1.0) <= 1e-4
        and abs(elas_energy - 1.0) <= 1e-4
    )
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {
        "tte_hours": tte,
        "tte_idle_hours": tte_idle,
        "tte_cold_hours": tte_cold,
        "tte_aged_hours": tte_aged,
        "tte_screen_plus20_hours": tte_screen_plus20,
        "elas_total_power": elas_power,
        "elas_energy": elas_energy,
        "elas_idle": elas["idle"],
        "elas_screen": elas["screen"],
        "elas_cpu": elas["cpu"],
        "elas_net": elas["net"],
        "elas_gps": elas["gps"],
        "elas_bg": elas["bg"],
    }
    return _finalize(
        dest, run_id, status, metrics, "energy_balance_soc_sensitivity", SOC_SENS_FIXTURE
    )


def run_soc_piecewise_pilot(
    output_root: Path, run_id: str = "soc-piecewise-pilot-001"
) -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    e_eff = effective_energy(SOC_PIECEWISE_FIXTURE["e_nom"], 1.0, 1.0)
    burst = tuple(tuple(row) for row in SOC_PIECEWISE_FIXTURE["burst_first"])
    idle = tuple(tuple(row) for row in SOC_PIECEWISE_FIXTURE["idle_first"])
    tte_burst = time_to_empty_piecewise(SOC_PIECEWISE_FIXTURE["soc0"], burst, e_eff)
    tte_idle = time_to_empty_piecewise(SOC_PIECEWISE_FIXTURE["soc0"], idle, e_eff)
    exact = soc_piecewise(
        SOC_PIECEWISE_FIXTURE["euler_t"],
        SOC_PIECEWISE_FIXTURE["soc0"],
        burst,
        e_eff,
    )
    approx = euler_soc_piecewise(
        steps=200,
        t_end=SOC_PIECEWISE_FIXTURE["euler_t"],
        soc0=SOC_PIECEWISE_FIXTURE["soc0"],
        segments=burst,
        e_eff=e_eff,
    )
    ok = (
        abs(tte_burst - SOC_PIECEWISE_FIXTURE["expected_burst"])
        <= SOC_PIECEWISE_FIXTURE["tolerance"]
        and abs(tte_idle - SOC_PIECEWISE_FIXTURE["expected_idle"])
        <= SOC_PIECEWISE_FIXTURE["tolerance"]
        and abs(exact - SOC_PIECEWISE_FIXTURE["expected_soc"])
        <= SOC_PIECEWISE_FIXTURE["tolerance"]
        and abs(approx - exact) <= SOC_PIECEWISE_FIXTURE["tolerance"]
    )
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {
        "tte_burst_first_hours": tte_burst,
        "tte_idle_first_hours": tte_idle,
        "soc_burst_at_1h": exact,
        "soc_euler_at_1h": approx,
        "order_ratio": tte_burst / tte_idle,
    }
    return _finalize(
        dest, run_id, status, metrics, "energy_balance_soc_piecewise", SOC_PIECEWISE_FIXTURE
    )


def run_lp_pilot(output_root: Path, run_id: str = "lp-pilot-001") -> RunResult:
    dest = _new_run_dir(output_root, run_id)
    x, y, objective = solve_two_var_lp(
        tuple(LP_FIXTURE["objective"]),
        [tuple(row) for row in LP_FIXTURE["constraints"]],
    )
    expected = LP_FIXTURE["expected"]
    ok = (
        abs(x - expected[0]) <= LP_FIXTURE["tolerance"]
        and abs(y - expected[1]) <= LP_FIXTURE["tolerance"]
        and abs(objective - expected[2]) <= LP_FIXTURE["tolerance"]
    )
    status = "SUCCEEDED" if ok else "FAILED"
    metrics = {"x": x, "y": y, "objective": objective}
    return _finalize(dest, run_id, status, metrics, "two_var_lp", LP_FIXTURE)


def _finalize(
    dest: Path,
    run_id: str,
    status: str,
    metrics: dict[str, float],
    engine: str,
    config: dict,
) -> RunResult:
    result_path = dest / "metrics.json"
    payload = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    result_path.write_text(payload, encoding="utf-8", newline="\n")
    config_bytes = json.dumps(config, sort_keys=True).encode("utf-8")
    manifest = {
        "run_id": run_id,
        "status": status,
        "git_commit": None,
        "dirty_worktree": True,
        "command": ["python", "-m", "tools.modeling", engine],
        "inputs": [],
        "config_sha256": sha256_bytes(config_bytes),
        "environment": {
            "os": platform.platform(),
            "python": sys.version.split()[0],
            "lock_sha256": hashlib.sha256(b"stdlib-only").hexdigest(),
            "packages_ref": "stdlib",
        },
        "solver": {"name": None, "version": None, "license": None},
        "randomness": {"seeds": [0], "deterministic_claim": "exact"},
        "outputs": [
            {"ref": result_path.name, "sha256": sha256_bytes(payload.encode("utf-8"))}
        ],
        "metrics": metrics,
        "engine": engine,
    }
    check = validate_manifest(manifest)
    if not check.ok:
        raise ValueError("; ".join(check.errors))
    (dest / "manifest.yaml").write_text(
        _to_yaml(manifest), encoding="utf-8", newline="\n"
    )
    return RunResult(
        run_id=run_id,
        status=status,
        metrics=metrics,
        output_dir=str(dest),
        message=engine,
    )


def _to_yaml(data: dict) -> str:
    import yaml

    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
