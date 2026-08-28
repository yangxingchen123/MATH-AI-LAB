"""Formal artifact manifest checks. Not Frozen Schema."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

from .models import CorrespondenceResult

REQUIRED_FIELDS = (
    "formal_ref",
    "natural_language_ref",
    "source_files",
    "toolchain",
    "build",
    "semantic_review_ref",
    "assumptions",
)
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_manifest(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def validate_manifest(data: dict, project_root: Path) -> CorrespondenceResult:
    errors: list[str] = []
    if not isinstance(data, dict):
        return CorrespondenceResult(ok=False, errors=["manifest must be a mapping"])
    for key in REQUIRED_FIELDS:
        if key not in data:
            errors.append(f"missing field: {key}")
    sources = data.get("source_files")
    if not isinstance(sources, list) or not sources:
        errors.append("source_files must be a non-empty list")
    else:
        for item in sources:
            if not isinstance(item, dict) or "ref" not in item or "sha256" not in item:
                errors.append("source_files entries need ref and sha256")
                continue
            path = project_root / str(item["ref"])
            if not path.is_file():
                errors.append(f"missing source: {item['ref']}")
            elif not SHA_RE.fullmatch(str(item["sha256"])):
                errors.append(f"bad sha256 for {item['ref']}")
            elif sha256_file(path) != item["sha256"]:
                errors.append(f"stale sha256 for {item['ref']}")
    toolchain = data.get("toolchain") or {}
    if isinstance(toolchain, dict):
        if not toolchain.get("lean"):
            errors.append("toolchain.lean is required")
        mathlib = toolchain.get("mathlib_commit")
        if mathlib not in {None, "", "none"} and not toolchain.get("lake_manifest_sha256"):
            errors.append("mathlib pin requires lake_manifest_sha256")
    build = data.get("build") or {}
    if isinstance(build, dict):
        status = build.get("status")
        if status not in {"SUCCEEDED", "FAILED", "CANCELLED", "CANDIDATE"}:
            errors.append("build.status must be SUCCEEDED|FAILED|CANCELLED|CANDIDATE")
        command = build.get("command")
        if command != ["lake", "build"]:
            errors.append("build.command must be lake build at project level")
    if not data.get("semantic_review_ref"):
        errors.append("semantic_review_ref is required")
    return CorrespondenceResult(ok=not errors, errors=errors)


def validate_manifest_file(path: Path, project_root: Path) -> CorrespondenceResult:
    try:
        data = load_manifest(path)
    except (OSError, yaml.YAMLError) as exc:
        return CorrespondenceResult(ok=False, errors=[str(exc)])
    return validate_manifest(data, project_root)
