"""Contest-facing SOC energy-balance helpers. Math lives in tools.modeling.engines."""

from __future__ import annotations

from tools.modeling.engines import (
    effective_energy,
    euler_soc,
    soc_constant_power,
    soc_piecewise,
    time_to_empty,
    time_to_empty_piecewise,
    total_power,
    tte_component_elasticity,
)

# ASSUMED order-of-magnitude phone pack; not a cited dataset (ASM-0006).
E_NOM_WH = 15.0


def scenario_power(name: str) -> float:
    profiles = {
        "idle": (0.3, 0.0, 0.0, 0.0, 0.0, 0.0),
        "baseline": (0.3, 1.5, 0.8, 0.2, 0.1, 0.1),
        "screen_heavy": (0.3, 2.5, 0.4, 0.2, 0.0, 0.1),
        "nav_gps": (0.3, 1.0, 0.6, 0.8, 0.8, 0.2),
    }
    if name not in profiles:
        raise KeyError(name)
    return total_power(*profiles[name])


def scenario_tte(name: str, *, soc0: float = 1.0, eta: float = 1.0, age: float = 1.0) -> float:
    return time_to_empty(soc0, scenario_power(name), effective_energy(E_NOM_WH, eta, age))


def baseline_parts() -> tuple[float, ...]:
    return (0.3, 1.5, 0.8, 0.2, 0.1, 0.1)


def baseline_elasticities() -> dict[str, float]:
    parts = baseline_parts()
    names = ("idle", "screen", "cpu", "net", "gps", "bg")
    return {name: tte_component_elasticity(parts, index) for index, name in enumerate(names)}


def write_sensitivity_svg(path) -> None:
    items = list(baseline_elasticities().items())
    width, height, pad = 80 + 90 * len(items), 280, 40
    vmax = max(abs(value) for _, value in items) or 1.0
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="16" y="24">TTE elasticity = -P_i / P (ASSUMED baseline)</text>',
    ]
    for index, (name, value) in enumerate(items):
        x = pad + index * 90
        h = abs(value) / vmax * 160
        y = height - pad - h
        parts.append(
            f'<rect x="{x}" y="{y:.2f}" width="48" height="{h:.2f}" fill="white" stroke="black"/>'
        )
        parts.append(f'<text x="{x + 24}" y="{height - 12}" text-anchor="middle">{name}</text>')
        parts.append(f'<text x="{x + 24}" y="{y - 8:.2f}" text-anchor="middle">{value:.3f}</text>')
    parts.append("</svg>\n")
    path.write_text("\n".join(parts), encoding="utf-8", newline="\n")


__all__ = [
    "E_NOM_WH",
    "effective_energy",
    "euler_soc",
    "scenario_power",
    "scenario_tte",
    "soc_constant_power",
    "soc_piecewise",
    "time_to_empty",
    "time_to_empty_piecewise",
    "total_power",
    "tte_component_elasticity",
    "write_sensitivity_svg",
]
