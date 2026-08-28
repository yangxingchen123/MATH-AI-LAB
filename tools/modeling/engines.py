"""Stdlib-only modeling engines. No solvers in the Foundation root environment."""

from __future__ import annotations

import math
from collections import deque


def shortest_path_length(edges: list[tuple[str, str]], source: str, target: str) -> int:
    graph: dict[str, list[str]] = {}
    for start, end in edges:
        graph.setdefault(start, []).append(end)
        graph.setdefault(end, [])
    if source == target:
        return 0
    seen = {source}
    queue: deque[tuple[str, int]] = deque([(source, 0)])
    while queue:
        node, dist = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt in seen:
                continue
            if nxt == target:
                return dist + 1
            seen.add(nxt)
            queue.append((nxt, dist + 1))
    raise ValueError(f"no path from {source} to {target}")


def quadratic_grid_minimum(lo: float, hi: float, steps: int) -> tuple[float, float]:
    if steps < 1 or hi < lo:
        raise ValueError("invalid grid")
    best_x = lo
    best_val = lo * lo
    width = hi - lo
    for index in range(steps + 1):
        x = lo + width * index / steps
        value = x * x
        if value < best_val:
            best_x = x
            best_val = value
    return best_x, best_val


def binomial_square(a: float, b: float) -> tuple[float, float]:
    expanded = a * a + 2 * a * b + b * b
    direct = (a + b) * (a + b)
    return direct, expanded


def euler_exponential(steps: int = 40, t: float = 1.0) -> tuple[float, float]:
    if steps < 1 or t < 0:
        raise ValueError("invalid ODE grid")
    h = t / steps
    y = 1.0
    for _ in range(steps):
        y = y + h * y
    return y, math.exp(t)


def ordinary_least_squares(xs: list[float], ys: list[float]) -> tuple[float, float]:
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("OLS needs at least two paired points")
    n = float(len(xs))
    xbar = sum(xs) / n
    ybar = sum(ys) / n
    varx = sum((x - xbar) ** 2 for x in xs)
    if varx == 0:
        raise ValueError("x values are not identifiable")
    cov = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys, strict=True))
    slope = cov / varx
    intercept = ybar - slope * xbar
    return intercept, slope


def mean_and_sample_variance(xs: list[float]) -> tuple[float, float]:
    if len(xs) < 2:
        raise ValueError("need at least two samples")
    n = float(len(xs))
    mean = sum(xs) / n
    variance = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, variance


def solve_two_var_lp(
    objective: tuple[float, float],
    constraints: list[tuple[float, float, float]],
) -> tuple[float, float, float]:
    c1, c2 = objective
    vertices = [(0.0, 0.0)]
    for a, b, rhs in constraints:
        if a == 0 and b == 0:
            continue
        if a != 0:
            vertices.append((rhs / a, 0.0))
        if b != 0:
            vertices.append((0.0, rhs / b))
    for i, (a1, b1, r1) in enumerate(constraints):
        for a2, b2, r2 in constraints[i + 1 :]:
            det = a1 * b2 - a2 * b1
            if abs(det) < 1e-15:
                continue
            x = (r1 * b2 - r2 * b1) / det
            y = (a1 * r2 - a2 * r1) / det
            vertices.append((x, y))

    def feasible(x: float, y: float) -> bool:
        if x < -1e-12 or y < -1e-12:
            return False
        return all(a * x + b * y <= rhs + 1e-12 for a, b, rhs in constraints)

    best: tuple[float, float, float] | None = None
    for x, y in vertices:
        if not feasible(x, y):
            continue
        value = c1 * x + c2 * y
        if best is None or value > best[2] + 1e-12:
            best = (x, y, value)
    if best is None:
        raise ValueError("LP is infeasible")
    return best


def effective_energy(e_nom: float, eta_temp: float, age: float) -> float:
    if e_nom <= 0 or eta_temp <= 0 or age <= 0:
        raise ValueError("effective energy factors must be positive")
    return e_nom * eta_temp * age


def total_power(
    idle: float,
    screen: float,
    cpu: float,
    net: float,
    gps: float,
    background: float,
) -> float:
    parts = (idle, screen, cpu, net, gps, background)
    if any(item < 0 for item in parts):
        raise ValueError("power components must be nonnegative")
    return float(sum(parts))


def soc_constant_power(t: float, soc0: float, power: float, e_eff: float) -> float:
    if e_eff <= 0:
        raise ValueError("e_eff must be positive")
    return soc0 - power * t / e_eff


def time_to_empty(soc0: float, power: float, e_eff: float) -> float:
    if soc0 < 0:
        raise ValueError("soc0 must be nonnegative")
    if power <= 0:
        raise ValueError("discharge power must be positive for time-to-empty")
    if e_eff <= 0:
        raise ValueError("e_eff must be positive")
    return e_eff * soc0 / power


def euler_soc(
    *,
    steps: int,
    t_end: float,
    soc0: float,
    power: float,
    e_eff: float,
) -> float:
    if steps < 1 or t_end < 0 or e_eff <= 0:
        raise ValueError("invalid SOC Euler grid")
    step = t_end / steps
    soc = soc0
    for _ in range(steps):
        soc = soc - step * power / e_eff
    return soc


def power_at(t: float, segments: tuple[tuple[float, float], ...]) -> float:
    if t < 0:
        raise ValueError("t must be nonnegative")
    if not segments:
        raise ValueError("segments must be nonempty")
    elapsed = 0.0
    for index, (power, duration) in enumerate(segments):
        if duration <= 0:
            raise ValueError("segment duration must be positive")
        if power < 0:
            raise ValueError("segment power must be nonnegative")
        end = elapsed + duration
        if t < end or index == len(segments) - 1:
            return power
        elapsed = end
    return segments[-1][0]


def soc_piecewise(
    t: float,
    soc0: float,
    segments: tuple[tuple[float, float], ...],
    e_eff: float,
) -> float:
    if e_eff <= 0:
        raise ValueError("e_eff must be positive")
    energy = e_eff * soc0
    elapsed = 0.0
    for index, (power, duration) in enumerate(segments):
        if duration <= 0 or power < 0:
            raise ValueError("invalid piecewise segment")
        end = elapsed + duration
        if t <= end or index == len(segments) - 1:
            energy -= power * (t - elapsed)
            return energy / e_eff
        energy -= power * duration
        elapsed = end
    return energy / e_eff


def time_to_empty_piecewise(
    soc0: float,
    segments: tuple[tuple[float, float], ...],
    e_eff: float,
) -> float:
    if soc0 < 0 or e_eff <= 0:
        raise ValueError("soc0 and e_eff must allow a discharge")
    if not segments:
        raise ValueError("segments must be nonempty")
    remaining = e_eff * soc0
    t = 0.0
    for index, (power, duration) in enumerate(segments):
        if duration <= 0 or power < 0:
            raise ValueError("invalid piecewise segment")
        last = index == len(segments) - 1
        span = duration if not last else float("inf")
        if power == 0:
            if last:
                raise ValueError("schedule never reaches empty")
            t += duration
            continue
        dt = remaining / power
        if dt <= span:
            return t + dt
        remaining -= power * duration
        t += duration
    raise ValueError("schedule ended before empty")


def euler_soc_piecewise(
    *,
    steps: int,
    t_end: float,
    soc0: float,
    segments: tuple[tuple[float, float], ...],
    e_eff: float,
) -> float:
    if steps < 1 or t_end < 0 or e_eff <= 0:
        raise ValueError("invalid piecewise Euler grid")
    step = t_end / steps
    soc = soc0
    t = 0.0
    for _ in range(steps):
        soc = soc - step * power_at(t, segments) / e_eff
        t += step
    return soc


def tte_component_elasticity(parts: tuple[float, ...], index: int) -> float:
    if index < 0 or index >= len(parts):
        raise ValueError("component index out of range")
    if any(item < 0 for item in parts):
        raise ValueError("power components must be nonnegative")
    total = float(sum(parts))
    if total <= 0:
        raise ValueError("total power must be positive")
    return -parts[index] / total


def relative_sensitivity(func, x: float, step: float = 1e-6) -> float:
    if x == 0:
        raise ValueError("relative sensitivity at x=0 is undefined")
    center = func(x)
    if center == 0:
        raise ValueError("relative sensitivity at f(x)=0 is undefined")
    derivative = (func(x + step) - func(x - step)) / (2 * step)
    return x * derivative / center
