"""Deterministic stdlib SVG / Mermaid generators. No matplotlib."""

from __future__ import annotations

import html
from typing import Any


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def numerical_uncertainty_svg(points: list[dict[str, float]], *, xlabel: str, ylabel: str) -> str:
    width, height = 480, 320
    pad = 48
    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    errs = [p.get("err", 0.0) for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin = min(y - e for y, e in zip(ys, errs, strict=True))
    ymax = max(y + e for y, e in zip(ys, errs, strict=True))
    if xmax == xmin:
        xmax = xmin + 1
    if ymax == ymin:
        ymax = ymin + 1

    def sx(x: float) -> float:
        return pad + (x - xmin) / (xmax - xmin) * (width - 2 * pad)

    def sy(y: float) -> float:
        return height - pad - (y - ymin) / (ymax - ymin) * (height - 2 * pad)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{pad}" y1="{height - pad}" x2="{width - pad}" y2="{height - pad}" stroke="black"/>',
        f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height - pad}" stroke="black"/>',
        f'<text x="{width / 2}" y="{height - 12}" text-anchor="middle">{_esc(xlabel)}</text>',
        f'<text x="16" y="{height / 2}" transform="rotate(-90 16 {height / 2})">{_esc(ylabel)}</text>',
    ]
    for i, point in enumerate(points):
        x = sx(point["x"])
        y = sy(point["y"])
        err = point.get("err", 0.0)
        y0, y1 = sy(point["y"] - err), sy(point["y"] + err)
        mark = "circle" if i % 2 == 0 else "rect"
        parts.append(
            f'<line x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" y2="{y1:.2f}" stroke="black"/>'
        )
        if mark == "circle":
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="black"/>')
        else:
            parts.append(
                f'<rect x="{x - 4:.2f}" y="{y - 4:.2f}" width="8" height="8" fill="none" stroke="black"/>'
            )
    parts.append(
        '<text x="360" y="36">legend: circle/square = series; bars = uncertainty</text>'
    )
    parts.append("</svg>\n")
    return "\n".join(parts)


def network_svg(nodes: list[str], edges: list[tuple[str, str]]) -> str:
    width, height = 420, 220
    positions = {
        name: (80 + i * 120, 110)
        for i, name in enumerate(nodes)
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        '<path d="M0,0 L0,6 L8,3 z" fill="black"/></marker></defs>',
    ]
    for start, end in edges:
        x1, y1 = positions[start]
        x2, y2 = positions[end]
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" marker-end="url(#arrow)"/>'
        )
    for name, (x, y) in positions.items():
        parts.append(f'<circle cx="{x}" cy="{y}" r="18" fill="white" stroke="black"/>')
        parts.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle">{_esc(name)}</text>')
    parts.append("</svg>\n")
    return "\n".join(parts)


def exact_function_svg(xs: list[float], ys: list[float], *, domain: str, formula: str) -> str:
    width, height, pad = 480, 320, 48
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax == xmin:
        xmax = xmin + 1
    if ymax == ymin:
        ymax = ymin + 1

    def sx(x: float) -> float:
        return pad + (x - xmin) / (xmax - xmin) * (width - 2 * pad)

    def sy(y: float) -> float:
        return height - pad - (y - ymin) / (ymax - ymin) * (height - 2 * pad)

    pts = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in zip(xs, ys, strict=True))
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            '<rect width="100%" height="100%" fill="white"/>',
            f'<polyline fill="none" stroke="black" stroke-dasharray="6 3" points="{pts}"/>',
            f'<text x="24" y="24">{_esc(formula)} domain {_esc(domain)}</text>',
            f'<text x="24" y="{height - 16}">x (dimensionless)</text>',
            f'<text x="16" y="160" transform="rotate(-90 16 160)">y (dimensionless)</text>',
            "</svg>\n",
        ]
    )


def sensitivity_svg(items: list[tuple[str, float]]) -> str:
    width, height, pad = 480, 280, 48
    values = [abs(value) for _, value in items] or [1.0]
    vmax = max(values) or 1.0
    bar_w = 48
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="24">sensitivity elasticity by parameter</text>',
    ]
    for index, (name, value) in enumerate(items):
        x = pad + index * 120
        h = abs(value) / vmax * 140
        y = height - pad - h
        parts.append(
            f'<rect x="{x}" y="{y:.2f}" width="{bar_w}" height="{h:.2f}" fill="white" stroke="black"/>'
        )
        parts.append(f'<text x="{x + bar_w / 2}" y="{height - 16}" text-anchor="middle">{_esc(name)}</text>')
        parts.append(
            f'<text x="{x + bar_w / 2}" y="{y - 8:.2f}" text-anchor="middle">{value:.3g}</text>'
        )
    parts.append("</svg>\n")
    return "\n".join(parts)


def architecture_mermaid(nodes: list[str], edges: list[tuple[str, str]]) -> str:
    lines = ["flowchart TD"]
    for node in nodes:
        lines.append(f"  {node}")
    for start, end in edges:
        lines.append(f"  {start} --> {end}")
    return "\n".join(lines) + "\n"


def architecture_svg(nodes: list[str], edges: list[tuple[str, str]]) -> str:
    width = 160 + 140 * len(nodes)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="160">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    pos = {name: (70 + i * 140, 80) for i, name in enumerate(nodes)}
    for start, end in edges:
        x1, y1 = pos[start]
        x2, y2 = pos[end]
        parts.append(f'<line x1="{x1 + 40}" y1="{y1}" x2="{x2 - 40}" y2="{y2}" stroke="black"/>')
    for name, (x, y) in pos.items():
        parts.append(
            f'<rect x="{x - 40}" y="{y - 20}" width="80" height="40" fill="white" stroke="black"/>'
        )
        parts.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle">{_esc(name)}</text>')
    parts.append("</svg>\n")
    return "\n".join(parts)


def semantic_payload(family: str, spec: dict[str, Any], extra: dict[str, Any] | None = None) -> dict:
    payload = {"family": family, "spec": spec}
    if extra:
        payload.update(extra)
    return payload
