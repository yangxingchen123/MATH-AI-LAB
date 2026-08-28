"""Figure manifest validation."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .constants import (
    AI_ENGINES,
    DETERMINISM_LEVELS,
    FAMILIES,
    REQUIRED_FIELDS,
    TRUST_LEVELS,
)
from .models import FigureValidationResult

SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def load_manifest(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def validate_manifest(data: dict) -> FigureValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return FigureValidationResult(ok=False, errors=["manifest must be a mapping"])
    for key in REQUIRED_FIELDS:
        if key not in data:
            errors.append(f"missing field: {key}")
    family = data.get("family")
    if family is not None and family not in FAMILIES:
        errors.append(f"unknown family: {family!r}")
    if not data.get("claim_refs"):
        errors.append("claim_refs must be non-empty")
    if family != "architecture" and not data.get("run_refs"):
        errors.append("run_refs must be non-empty except architecture diagrams")
    for group in ("source_code", "config"):
        item = data.get(group)
        if item is None:
            continue
        if not isinstance(item, dict) or "ref" not in item or "sha256" not in item:
            errors.append(f"{group} needs ref and sha256")
        elif not (isinstance(item.get("sha256"), str) and SHA_RE.fullmatch(item["sha256"])):
            errors.append(f"{group}.sha256 must be 64 lowercase hex characters")
    for group in ("inputs", "outputs"):
        items = data.get(group)
        if items is None:
            continue
        if not isinstance(items, list) or not items:
            errors.append(f"{group} must be a non-empty list")
            continue
        for item in items:
            if not isinstance(item, dict) or "ref" not in item or "sha256" not in item:
                errors.append(f"{group} entries need ref and sha256")
            elif not SHA_RE.fullmatch(str(item.get("sha256", ""))):
                errors.append(f"{group} sha256 must be 64 lowercase hex characters")
    engine = data.get("engine")
    if isinstance(engine, dict):
        name = str(engine.get("name") or "")
        if name.lower() in AI_ENGINES and family not in {None, "concept"}:
            errors.append("AI image engine cannot be used for exact figure families")
        if name.lower() in AI_ENGINES and data.get("trust_level") == "FORMAL":
            errors.append("AI concept illustration cannot be FORMAL")
    checks = data.get("semantic_checks")
    if checks is not None:
        if not isinstance(checks, dict):
            errors.append("semantic_checks must be a mapping")
        else:
            for key in ("units", "legend", "grayscale", "color_vision"):
                if key not in checks:
                    errors.append(f"semantic_checks missing {key}")
            if family == "numerical_uncertainty" and checks.get("uncertainty") not in {
                "present",
                "not_applicable",
            }:
                errors.append("numerical figures must declare uncertainty")
    det = data.get("determinism")
    if det is not None and det not in DETERMINISM_LEVELS:
        errors.append(f"illegal determinism: {det!r}")
    trust = data.get("trust_level")
    if trust is not None and trust not in TRUST_LEVELS:
        errors.append(f"illegal trust_level: {trust!r}")
    return FigureValidationResult(ok=not errors, errors=errors, warnings=warnings)


def validate_manifest_file(path: Path) -> FigureValidationResult:
    try:
        data = load_manifest(path)
    except (OSError, yaml.YAMLError) as exc:
        return FigureValidationResult(ok=False, errors=[str(exc)])
    return validate_manifest(data)
