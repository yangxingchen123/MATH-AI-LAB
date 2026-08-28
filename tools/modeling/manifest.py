"""Validate modeling run manifests."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

from .constants import ALLOWED_STATUS, REQUIRED_MANIFEST_FIELDS, SHA256_LEN
from .models import ManifestValidationResult

SHA_RE = re.compile(rf"^[0-9a-f]{{{SHA256_LEN}}}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_manifest(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def validate_manifest(data: dict) -> ManifestValidationResult:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ManifestValidationResult(ok=False, errors=["manifest must be a mapping"])
    for key in REQUIRED_MANIFEST_FIELDS:
        if key not in data:
            errors.append(f"missing field: {key}")
    status = data.get("status")
    if status is not None and status not in ALLOWED_STATUS:
        errors.append(f"illegal status: {status!r}")
    command = data.get("command")
    if command is not None and not (
        isinstance(command, list) and all(isinstance(item, str) for item in command)
    ):
        errors.append("command must be a list of strings")
    config_hash = data.get("config_sha256")
    if config_hash is not None and not (
        isinstance(config_hash, str) and SHA_RE.fullmatch(config_hash)
    ):
        errors.append("config_sha256 must be 64 lowercase hex characters")
    for group_name in ("inputs", "outputs"):
        items = data.get(group_name)
        if items is None:
            continue
        if not isinstance(items, list):
            errors.append(f"{group_name} must be a list")
            continue
        for item in items:
            if not isinstance(item, dict) or "ref" not in item or "sha256" not in item:
                errors.append(f"{group_name} entries need ref and sha256")
                continue
            if not (isinstance(item["sha256"], str) and SHA_RE.fullmatch(item["sha256"])):
                errors.append(f"{group_name} sha256 must be 64 lowercase hex characters")
    env = data.get("environment")
    if env is not None:
        if not isinstance(env, dict):
            errors.append("environment must be a mapping")
        else:
            for key in ("os", "python", "lock_sha256"):
                if key not in env:
                    errors.append(f"environment missing {key}")
            lock = env.get("lock_sha256")
            if lock is not None and not (isinstance(lock, str) and SHA_RE.fullmatch(lock)):
                errors.append("environment.lock_sha256 must be 64 lowercase hex characters")
    randomness = data.get("randomness")
    if randomness is not None:
        if not isinstance(randomness, dict) or "seeds" not in randomness:
            errors.append("randomness must include seeds")
        elif randomness.get("deterministic_claim") not in {
            None,
            "exact",
            "tolerance",
            "statistical",
        }:
            errors.append("illegal deterministic_claim")
    solver = data.get("solver")
    if solver is not None and isinstance(solver, dict):
        if solver.get("name") and not solver.get("license"):
            errors.append("non-default solver requires license")
    if data.get("status") == "SUCCEEDED" and not data.get("outputs"):
        errors.append("SUCCEEDED run must list outputs")
    return ManifestValidationResult(ok=not errors, errors=errors)


def validate_manifest_file(path: Path) -> ManifestValidationResult:
    try:
        data = load_manifest(path)
    except (OSError, yaml.YAMLError) as exc:
        return ManifestValidationResult(ok=False, errors=[str(exc)])
    return validate_manifest(data)
