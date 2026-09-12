"""Operating-conditions preflight. Does not run instance demos like P001."""

from __future__ import annotations

import sys

from tools.lean_formalization.build import lake_available, toolchain_present

from .constants import (
    AGENTS_PATH,
    CONTRACT_VERSION,
    FROZEN_SCHEMA_PATH,
    LOCKFILE_PATH,
    PROJECT_RULES_PATH,
    REPO_ROOT,
    SPEC_PATH,
    USAGE_GUIDE_PATH,
)
from .inventory import scan_inventory
from .protocol import load_protocol, validate_protocol
from .exploration import layer_health

FORBIDDEN: tuple[str, ...] = (
    "write_frozen_schema",
    "auto_create_knowledge",
    "auto_create_method",
    "forge_attempt",
    "claim_四大",
    "claim_v2.2_VERIFIED",
    "fail_core_when_lake_missing",
    "parallel_research_formal_experiments_tree",
    "new_problem_on_infra_task",
)


def operate() -> dict:
    inventory = scan_inventory(REPO_ROOT)
    protocol_errors = validate_protocol(load_protocol())
    lean_status = _lean_status()
    health = layer_health()
    checks = [
        _check("inventory", inventory["key_roots_complete"], inventory["missing"] or "all key roots present"),
        _check("protocol", protocol_errors == [], protocol_errors or "conversation policy loaded"),
        _check("frozen_schema_present", FROZEN_SCHEMA_PATH.is_file(), str(FROZEN_SCHEMA_PATH.name)),
        _check("project_rules_present", PROJECT_RULES_PATH.is_file(), str(PROJECT_RULES_PATH.name)),
        _check("agents_present", AGENTS_PATH.is_file(), str(AGENTS_PATH.name)),
        _check("spec_present", SPEC_PATH.is_file(), str(SPEC_PATH.name)),
        _check("usage_guide_present", USAGE_GUIDE_PATH.is_file(), str(USAGE_GUIDE_PATH.name)),
        _check("lockfile_present", LOCKFILE_PATH.is_file(), str(LOCKFILE_PATH.name)),
        {
            "name": "lean_sidecar",
            "status": lean_status,
            "detail": "READY if lake+toolchain present; else DEGRADED; never FAIL Core",
        },
        _check(
            "python_runtime",
            True,
            f"{sys.version_info.major}.{sys.version_info.minor}",
        ),
        _check("exploration_layer", health["ok"], health["detail"]),
    ]
    blocking = [item for item in checks if item["status"] == "FAIL"]
    status = "FAIL" if blocking else "PASS"
    if status == "PASS" and lean_status == "DEGRADED":
        status = "DEGRADED"
    return {
        "contract_version": CONTRACT_VERSION,
        "status": status,
        "core_impact": False,
        "writes_source": False,
        "layer": "operating_conditions",
        "instance_calibration_required": False,
        "forbidden": list(FORBIDDEN),
        "next": (
            "route the current user task; do not emit a new P00xx or Lean theorem "
            "unless the user asked for a math problem"
        ),
        "checks": checks,
        "note": "Sidecar. Operating layer only. Does not claim 四大 or v2.2 VERIFIED.",
    }


def _lean_status() -> str:
    if lake_available() and toolchain_present():
        return "READY"
    return "DEGRADED"


def _check(name: str, ok: bool, detail: object) -> dict:
    return {
        "name": name,
        "status": "PASS" if ok else "FAIL",
        "detail": str(detail),
    }
