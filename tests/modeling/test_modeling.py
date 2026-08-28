from pathlib import Path

from tools.modeling.engines import (
    binomial_square,
    euler_exponential,
    quadratic_grid_minimum,
    shortest_path_length,
)
from tools.modeling.manifest import validate_manifest
from tools.modeling.runner import (
    run_network_pilot,
    run_ode_pilot,
    run_quadratic_pilot,
    run_symbolic_pilot,
)


def test_known_answer_network():
    assert shortest_path_length([("A", "B"), ("B", "C")], "A", "C") == 2


def test_known_answer_quadratic():
    x, value = quadratic_grid_minimum(0.0, 1.0, 20)
    assert abs(x) < 1e-12
    assert abs(value) < 1e-12


def test_known_answer_symbolic_and_ode():
    direct, expanded = binomial_square(3.0, 4.0)
    assert abs(direct - expanded) < 1e-12
    approx, exact = euler_exponential(40, 1.0)
    assert abs(approx - exact) <= 0.05


def test_manifest_requires_hashes():
    result = validate_manifest({"run_id": "x", "status": "QUEUED"})
    assert result.ok is False
    assert any("missing field" in item for item in result.errors)


def test_succeeded_requires_outputs():
    data = {
        "run_id": "r1",
        "status": "SUCCEEDED",
        "command": ["python"],
        "inputs": [],
        "config_sha256": "a" * 64,
        "environment": {
            "os": "test",
            "python": "3.13",
            "lock_sha256": "b" * 64,
        },
        "randomness": {"seeds": [0], "deterministic_claim": "exact"},
        "outputs": [],
    }
    assert validate_manifest(data).ok is False


def test_solver_without_license_rejected():
    data = {
        "run_id": "r1",
        "status": "FAILED",
        "command": ["python"],
        "inputs": [],
        "config_sha256": "a" * 64,
        "environment": {
            "os": "test",
            "python": "3.13",
            "lock_sha256": "b" * 64,
        },
        "randomness": {"seeds": [0], "deterministic_claim": "exact"},
        "outputs": [],
        "solver": {"name": "secret-solver"},
    }
    result = validate_manifest(data)
    assert result.ok is False
    assert any("license" in item for item in result.errors)


def test_pilots_write_immutable_runs(tmp_path: Path):
    net = run_network_pilot(tmp_path, "net-1")
    opt = run_quadratic_pilot(tmp_path, "opt-1")
    sym = run_symbolic_pilot(tmp_path, "sym-1")
    ode = run_ode_pilot(tmp_path, "ode-1")
    assert net.status == "SUCCEEDED"
    assert opt.status == "SUCCEEDED"
    assert sym.status == "SUCCEEDED"
    assert ode.status == "SUCCEEDED"
    assert (tmp_path / "net-1" / "manifest.yaml").is_file()
    assert (tmp_path / "opt-1" / "metrics.json").is_file()
    try:
        run_network_pilot(tmp_path, "net-1")
        raised = False
    except FileExistsError:
        raised = True
    assert raised is True


def test_cli_doctor():
    from tools.modeling.cli import main

    assert main(["doctor"]) == 0
    assert main(["run", "--help"]) == 0
