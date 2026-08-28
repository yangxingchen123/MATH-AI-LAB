"""Semantic and accessibility checks for figure manifests and SVG."""

from __future__ import annotations

from .constants import AI_ENGINES
from .models import FigureValidationResult


def check_semantic(
    manifest: dict,
    svg_text: str,
    semantic: dict | None = None,
) -> FigureValidationResult:
    errors: list[str] = []
    family = manifest.get("family")
    checks = manifest.get("semantic_checks") or {}
    payload = semantic or {}
    spec = payload.get("spec") if isinstance(payload.get("spec"), dict) else {}
    if not checks.get("units"):
        errors.append("units check not recorded")
    if not checks.get("legend"):
        errors.append("legend check not recorded")
    if family == "numerical_uncertainty":
        if checks.get("uncertainty") != "present":
            errors.append("uncertainty encoding missing")
        if "uncertainty" not in svg_text.lower():
            errors.append("numerical SVG must encode uncertainty")
        xlabel = str(spec.get("xlabel") or "")
        ylabel = str(spec.get("ylabel") or "")
        if xlabel and xlabel not in svg_text:
            errors.append("xlabel missing from SVG")
        if ylabel and ylabel not in svg_text:
            errors.append("ylabel missing from SVG")
        if not xlabel and "dimensionless" not in svg_text.lower() and "(" not in svg_text:
            errors.append("axis labels must include units")
    if family == "network":
        identities = payload.get("identities") or spec.get("nodes") or []
        missing = [name for name in identities if str(name) not in svg_text]
        if missing:
            errors.append("network identity missing from SVG: " + ", ".join(map(str, missing)))
        elif not identities:
            errors.append("network identities not recorded")
    if not checks.get("grayscale"):
        errors.append("grayscale check not recorded")
    if not checks.get("color_vision"):
        errors.append("color_vision check not recorded")
    if 'fill="red"' in svg_text and "stroke-dasharray" not in svg_text:
        errors.append("color is the only encoding")
    return FigureValidationResult(ok=not errors, errors=errors)


def check_ai_misuse(manifest: dict) -> FigureValidationResult:
    errors: list[str] = []
    engine = manifest.get("engine") or {}
    name = str(engine.get("name") or "").lower()
    family = manifest.get("family")
    if name in AI_ENGINES and family != "concept":
        errors.append("AI illustration used as exact figure")
    return FigureValidationResult(ok=not errors, errors=errors)
