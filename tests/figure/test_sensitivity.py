from pathlib import Path

from tools.figure.renderer import render_sensitivity


def test_sensitivity_figure_is_traceable(tmp_path: Path):
    figure = render_sensitivity(tmp_path, "sens-1")
    svg = figure.svg_path.read_text(encoding="utf-8")
    assert "sensitivity" in svg.lower()
    assert "elasticity" in svg.lower()
    assert figure.family == "sensitivity"
