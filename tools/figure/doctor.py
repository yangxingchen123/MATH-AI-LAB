"""Figure Sidecar availability. Missing engines never fail Core math paths."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from .constants import CONTRACT_VERSION
from .renderer import render_network


def doctor() -> dict:
    errors: list[str] = []
    with TemporaryDirectory() as tmp:
        try:
            figure = render_network(Path(tmp), "net-pilot-001")
            if not figure.svg_path.is_file():
                errors.append("network pilot did not write SVG")
        except Exception as exc:
            errors.append(str(exc))
    return {
        "status": "PASS" if not errors else "FAIL",
        "engine": "stdlib-svg",
        "matplotlib": "not-required",
        "plotly": "not-required",
        "manim": "not-required",
        "contract_version": CONTRACT_VERSION,
        "errors": errors,
        "note": "Core figure pilots use stdlib SVG/Mermaid; heavy renderers stay optional Sidecars.",
    }
