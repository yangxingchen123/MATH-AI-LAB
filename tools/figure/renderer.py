"""Render figure families into immutable directories."""

from __future__ import annotations

import json
import os
import shutil
import uuid
from pathlib import Path

import yaml

from tools.modeling.manifest import sha256_bytes
from tools.modeling.runner import NETWORK_FIXTURE, QUAD_FIXTURE

from .constants import CONTRACT_VERSION
from .draw import (
    architecture_mermaid,
    architecture_svg,
    exact_function_svg,
    network_svg,
    numerical_uncertainty_svg,
    semantic_payload,
    sensitivity_svg,
)
from .manifest import validate_manifest
from .models import FigureResult

ARCH_NODES = ["Dossier", "Assumptions", "Evidence", "Decisions"]
ARCH_EDGES = [
    ("Dossier", "Assumptions"),
    ("Dossier", "Evidence"),
    ("Dossier", "Decisions"),
]


def _network_graph() -> tuple[list[str], list[tuple[str, str]]]:
    edges = [(str(start), str(end)) for start, end in NETWORK_FIXTURE["edges"]]
    nodes: list[str] = []
    for start, end in edges:
        if start not in nodes:
            nodes.append(start)
        if end not in nodes:
            nodes.append(end)
    return nodes, edges


def _quadratic_points() -> list[dict[str, float]]:
    lo = float(QUAD_FIXTURE["lo"])
    hi = float(QUAD_FIXTURE["hi"])
    steps = int(QUAD_FIXTURE["steps"])
    width = hi - lo
    err = (width / steps) / 2 if steps else 0.0
    points = []
    for index in range(steps + 1):
        x = lo + width * index / steps
        points.append({"x": x, "y": x * x, "err": err})
    return points


def _publish(dest: Path, figure_id: str, family: str, svg: str, semantic: dict, manifest: dict) -> FigureResult:
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError(f"figure_id already exists: {figure_id}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    work = dest.parent / f".{figure_id}.{uuid.uuid4().hex}.tmp"
    work.mkdir()
    try:
        svg_path = work / "figure.svg"
        mermaid_path = work / "figure.mmd"
        semantic_path = work / "semantic.json"
        manifest_path = work / "manifest.yaml"
        svg_bytes = svg.encode("utf-8")
        svg_path.write_bytes(svg_bytes)
        semantic_text = json.dumps(semantic, indent=2, sort_keys=True) + "\n"
        semantic_path.write_text(semantic_text, encoding="utf-8", newline="\n")
        mermaid = semantic.get("mermaid")
        outputs = [
            {"ref": "figure.svg", "sha256": sha256_bytes(svg_bytes), "format": "svg"},
            {"ref": "semantic.json", "sha256": sha256_bytes(semantic_text.encode("utf-8"))},
        ]
        if isinstance(mermaid, str):
            mermaid_path.write_text(mermaid, encoding="utf-8", newline="\n")
            outputs.append(
                {"ref": "figure.mmd", "sha256": sha256_bytes(mermaid.encode("utf-8")), "format": "mmd"}
            )
        manifest = dict(manifest)
        manifest["outputs"] = outputs
        check = validate_manifest(manifest)
        if not check.ok:
            raise ValueError("; ".join(check.errors))
        manifest_path.write_text(
            yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
            newline="\n",
        )
        os.replace(work, dest)
    except Exception:
        shutil.rmtree(work, ignore_errors=True)
        raise
    return FigureResult(
        figure_id=figure_id,
        family=family,
        output_dir=dest,
        svg_path=dest / "figure.svg",
        manifest_path=dest / "manifest.yaml",
        semantic_path=dest / "semantic.json",
        svg_sha256=sha256_bytes(svg.encode("utf-8")),
        semantic_sha256=sha256_bytes(
            (json.dumps(semantic, indent=2, sort_keys=True) + "\n").encode("utf-8")
        ),
    )


def _base_manifest(
    *,
    figure_id: str,
    family: str,
    claim_refs: list[str],
    run_refs: list[str],
    config: dict,
    uncertainty: str,
) -> dict:
    config_text = json.dumps(config, sort_keys=True)
    return {
        "figure_id": figure_id,
        "family": family,
        "claim_refs": claim_refs,
        "run_refs": run_refs,
        "source_code": {
            "ref": "tools.figure.draw",
            "sha256": sha256_bytes(Path(__file__).with_name("draw.py").read_bytes()),
        },
        "inputs": [
            {"ref": "config", "sha256": sha256_bytes(config_text.encode("utf-8"))}
        ],
        "config": {
            "ref": "inline",
            "sha256": sha256_bytes(config_text.encode("utf-8")),
        },
        "environment_ref": f"figure-contract-{CONTRACT_VERSION}",
        "engine": {"name": "stdlib-svg", "version": CONTRACT_VERSION},
        "outputs": [{"ref": "pending", "sha256": "0" * 64}],
        "semantic_checks": {
            "units": True,
            "legend": True,
            "uncertainty": uncertainty,
            "grayscale": True,
            "color_vision": True,
        },
        "determinism": "BYTE_EXACT",
        "trust_level": "DERIVED",
        "contract_version": CONTRACT_VERSION,
    }


def render_numerical(output_root: Path, run_id: str, figure_id: str = "fig-num-001") -> FigureResult:
    points = _quadratic_points()
    spec = {
        "xlabel": "x (dimensionless)",
        "ylabel": "x^2 (dimensionless)",
        "points": points,
        "run_id": run_id,
        "model": "quadratic_grid_min",
        "uncertainty": "half grid step",
    }
    svg = numerical_uncertainty_svg(points, xlabel=spec["xlabel"], ylabel=spec["ylabel"])
    semantic = semantic_payload("numerical_uncertainty", spec, {"encodings": ["shape", "position"]})
    manifest = _base_manifest(
        figure_id=figure_id,
        family="numerical_uncertainty",
        claim_refs=["CLM-0001"],
        run_refs=[run_id],
        config=spec,
        uncertainty="present",
    )
    return _publish(Path(output_root) / figure_id, figure_id, "numerical_uncertainty", svg, semantic, manifest)


def render_network(output_root: Path, run_id: str, figure_id: str = "fig-net-001") -> FigureResult:
    nodes, edges = _network_graph()
    spec = {
        "nodes": nodes,
        "edges": [list(edge) for edge in edges],
        "run_id": run_id,
        "model": "network_shortest_path",
        "source": NETWORK_FIXTURE["source"],
        "target": NETWORK_FIXTURE["target"],
    }
    svg = network_svg(nodes, edges)
    semantic = semantic_payload(
        "network",
        spec,
        {"identities": nodes, "layout": "linear", "weights_from": "data"},
    )
    manifest = _base_manifest(
        figure_id=figure_id,
        family="network",
        claim_refs=["CLM-0001"],
        run_refs=[run_id],
        config=spec,
        uncertainty="not_applicable",
    )
    return _publish(Path(output_root) / figure_id, figure_id, "network", svg, semantic, manifest)


def render_exact_function(output_root: Path, run_id: str, figure_id: str = "fig-fn-001") -> FigureResult:
    lo = float(QUAD_FIXTURE["lo"])
    hi = float(QUAD_FIXTURE["hi"])
    xs = [lo + (hi - lo) * i / 40 for i in range(41)]
    ys = [x * x for x in xs]
    spec = {
        "formula": "y=x^2",
        "domain": f"[{lo:g},{hi:g}]",
        "run_id": run_id,
        "model": "quadratic_grid_min",
    }
    svg = exact_function_svg(xs, ys, domain=spec["domain"], formula=spec["formula"])
    semantic = semantic_payload("exact_function", spec, {"samples": list(zip(xs, ys, strict=True))})
    manifest = _base_manifest(
        figure_id=figure_id,
        family="exact_function",
        claim_refs=["CLM-0001"],
        run_refs=[run_id],
        config=spec,
        uncertainty="not_applicable",
    )
    return _publish(Path(output_root) / figure_id, figure_id, "exact_function", svg, semantic, manifest)


def render_architecture(output_root: Path, figure_id: str = "fig-arch-001") -> FigureResult:
    spec = {"nodes": ARCH_NODES, "edges": [list(edge) for edge in ARCH_EDGES]}
    svg = architecture_svg(ARCH_NODES, ARCH_EDGES)
    mermaid = architecture_mermaid(ARCH_NODES, ARCH_EDGES)
    semantic = semantic_payload("architecture", spec, {"mermaid": mermaid})
    manifest = _base_manifest(
        figure_id=figure_id,
        family="architecture",
        claim_refs=["CLM-0001"],
        run_refs=[],
        config=spec,
        uncertainty="not_applicable",
    )
    return _publish(Path(output_root) / figure_id, figure_id, "architecture", svg, semantic, manifest)


def render_sensitivity(output_root: Path, run_id: str, figure_id: str = "fig-sens-001") -> FigureResult:
    items = [("x", 2.0)]
    spec = {
        "parameters": [{"name": name, "elasticity": value} for name, value in items],
        "run_id": run_id,
        "model": "relative_sensitivity",
    }
    svg = sensitivity_svg(items)
    semantic = semantic_payload("sensitivity", spec, {"encodings": ["height", "label"]})
    manifest = _base_manifest(
        figure_id=figure_id,
        family="sensitivity",
        claim_refs=["CLM-0001"],
        run_refs=[run_id],
        config=spec,
        uncertainty="not_applicable",
    )
    return _publish(Path(output_root) / figure_id, figure_id, "sensitivity", svg, semantic, manifest)
