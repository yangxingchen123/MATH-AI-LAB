from pathlib import Path

import yaml

from tools.figure.checks import check_ai_misuse, check_semantic
from tools.figure.constants import GATE_METRIC_NAMES
from tools.figure.gate import evaluate_gate
from tools.figure.manifest import validate_manifest
from tools.figure.renderer import (
    render_architecture,
    render_exact_function,
    render_network,
    render_numerical,
)
from tools.modeling.runner import NETWORK_FIXTURE


def test_manifest_requires_claims_and_hashes():
    result = validate_manifest({"figure_id": "f1", "family": "network"})
    assert result.ok is False
    assert any("missing field" in item for item in result.errors)


def test_architecture_may_omit_run_refs():
    data = _valid_manifest("architecture")
    data["run_refs"] = []
    assert validate_manifest(data).ok is True


def test_numerical_requires_run_refs():
    data = _valid_manifest("numerical_uncertainty")
    data["run_refs"] = []
    assert validate_manifest(data).ok is False


def test_ai_engine_rejected_for_exact_family():
    data = _valid_manifest("numerical_uncertainty")
    data["engine"] = {"name": "ai-image"}
    result = validate_manifest(data)
    assert result.ok is False
    assert any("AI image" in item for item in result.errors)
    assert check_ai_misuse(data).ok is False


def test_four_family_pilots_are_immutable(tmp_path: Path):
    num = render_numerical(tmp_path, "opt-1")
    net = render_network(tmp_path, "net-1")
    fn = render_exact_function(tmp_path, "opt-1")
    arch = render_architecture(tmp_path)
    for figure in (num, net, fn, arch):
        assert figure.svg_path.is_file()
        assert figure.manifest_path.is_file()
        svg = figure.svg_path.read_text(encoding="utf-8")
        manifest = yaml.safe_load(figure.manifest_path.read_text(encoding="utf-8"))
        semantic = yaml.safe_load(figure.semantic_path.read_text(encoding="utf-8"))
        assert check_semantic(manifest, svg, semantic).ok is True
    try:
        render_numerical(tmp_path, "opt-1")
        raised = False
    except FileExistsError:
        raised = True
    assert raised is True
    assert (tmp_path / "fig-arch-001" / "figure.mmd").is_file()
    svg_num = num.svg_path.read_text(encoding="utf-8")
    svg_net = net.svg_path.read_text(encoding="utf-8")
    assert "veh" not in svg_num
    assert "dimensionless" in svg_num
    assert "uncertainty" in svg_num
    for node in ("A", "B", "C"):
        assert node in svg_net
    assert NETWORK_FIXTURE["source"] in svg_net


def test_rebuild_is_byte_exact(tmp_path: Path):
    first = render_network(tmp_path / "a", "net-1")
    second = render_network(tmp_path / "b", "net-1")
    assert first.svg_sha256 == second.svg_sha256


def test_gate_metric_names_are_frozen():
    report = evaluate_gate()
    names = [item["name"] for item in report["metrics"]]
    assert names == list(GATE_METRIC_NAMES)
    assert report["status"] == "PASS"


def test_cli_doctor():
    from tools.figure.cli import main

    assert main(["doctor"]) == 0
    assert main(["gate", "--help"]) == 0


def test_network_identities_required_in_svg():
    manifest = _valid_manifest("network")
    semantic = {"identities": ["A", "B"], "spec": {"nodes": ["A", "B"]}}
    result = check_semantic(manifest, "<svg></svg>", semantic)
    assert result.ok is False
    assert any("identity" in item for item in result.errors)


def test_failed_publish_does_not_leave_figure_dir(tmp_path: Path, monkeypatch):
    from tools.figure import renderer
    from tools.figure.models import FigureValidationResult

    def boom(_manifest):
        return FigureValidationResult(ok=False, errors=["nope"])

    monkeypatch.setattr(renderer, "validate_manifest", boom)
    try:
        render_network(tmp_path, "net-1")
        raised = False
    except ValueError:
        raised = True
    assert raised is True
    assert not (tmp_path / "fig-net-001").exists()
    leftovers = list(tmp_path.glob(".*tmp")) + list(tmp_path.glob(".fig-*"))
    assert leftovers == []


def _valid_manifest(family: str) -> dict:
    digest = "a" * 64
    return {
        "figure_id": "fig-1",
        "family": family,
        "claim_refs": ["CLM-0001"],
        "run_refs": ["run-1"],
        "source_code": {"ref": "tools.figure.draw", "sha256": digest},
        "inputs": [{"ref": "data.json", "sha256": digest}],
        "config": {"ref": "config", "sha256": digest},
        "engine": {"name": "stdlib-svg", "version": "1.5"},
        "outputs": [{"ref": "figure.svg", "sha256": digest}],
        "semantic_checks": {
            "units": True,
            "legend": True,
            "uncertainty": "present" if family == "numerical_uncertainty" else "not_applicable",
            "grayscale": True,
            "color_vision": True,
        },
        "determinism": "BYTE_EXACT",
        "trust_level": "DERIVED",
    }
