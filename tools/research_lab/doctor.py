"""Read-only v2.2-lab doctor. Never blocks Core mathematics paths."""

from __future__ import annotations

import yaml

from .constants import (
    CONTRACT_VERSION,
    CORRESPONDENCE_PATH,
    FIDELITY_FIXTURE,
    LOCKFILE_PATH,
    PROBLEM_REGISTRY,
    REPO_ROOT,
    SPEC_PATH,
    USAGE_GUIDE_PATH,
)
from .conjecture import load_all_conjectures, validate_conjecture
from .evaluators.sum_free import evaluate_candidate, max_sum_free_size, upper_half_construction
from .exploration import layer_health
from .fidelity import evaluate_suite
from .inventory import scan_inventory
from .protocol import load_protocol, validate_protocol
from .registry import load_record, validate_record
from .search import greedy_sum_free

REQUIRED_CORRESPONDENCE_IDS = ("ANL-001", "DISC-006")


def doctor() -> dict:
    inventory = scan_inventory(REPO_ROOT)
    fidelity = evaluate_suite(FIDELITY_FIXTURE) if FIDELITY_FIXTURE.is_file() else None
    correspondence = CORRESPONDENCE_PATH.is_file()
    correspondence_ids_ok = _correspondence_ids_present()
    protocol_ok = validate_protocol(load_protocol()) == []
    lockfile_ok = LOCKFILE_PATH.is_file()
    conjectures = load_all_conjectures()
    conjectures_ok = bool(conjectures) and all(validate_conjecture(item) == [] for item in conjectures)
    n = 10
    construction = upper_half_construction(n)
    known = len(construction) == max_sum_free_size(n)
    blind = evaluate_candidate(n, greedy_sum_free(n)).get("optimal") is True
    problem_ok = False
    if PROBLEM_REGISTRY.is_file():
        problem_ok = validate_record(load_record(PROBLEM_REGISTRY)) == []
    status = "PASS"
    if not USAGE_GUIDE_PATH.is_file() or not SPEC_PATH.is_file():
        status = "FAIL"
    elif not inventory["key_roots_complete"] or fidelity is None or not fidelity["gold_clean"]:
        status = "FAIL"
    elif not fidelity.get("equivalents_clean", True):
        status = "FAIL"
    elif not protocol_ok or not lockfile_ok or not conjectures_ok:
        status = "FAIL"
    elif not known or not correspondence or not correspondence_ids_ok or not blind or not problem_ok:
        status = "FAIL"
    elif not layer_health()["ok"]:
        status = "FAIL"
    else:
        from .backlog import evaluate_backlog

        if not evaluate_backlog().get("ok"):
            status = "FAIL"
    return {
        "status": status,
        "core_impact": False,
        "contract_version": CONTRACT_VERSION,
        "usage_guide": USAGE_GUIDE_PATH.is_file(),
        "spec": SPEC_PATH.is_file(),
        "inventory_complete": inventory["key_roots_complete"],
        "sum_free_known_bound": known,
        "blind_search_optimal": blind,
        "problem_registry_ok": problem_ok,
        "correspondence_present": correspondence,
        "correspondence_ids_ok": correspondence_ids_ok,
        "protocol_ok": protocol_ok,
        "lockfile_ok": lockfile_ok,
        "conjectures_ok": conjectures_ok,
        "exploration_layer_ok": layer_health()["ok"],
        "instance_calibration_required_for_operate": False,
        "fidelity": fidelity,
        "note": "Sidecar. Does not write Source. Does not claim 四大 or v2.2 VERIFIED.",
    }


def _correspondence_ids_present() -> bool:
    if not CORRESPONDENCE_PATH.is_file():
        return False
    data = yaml.safe_load(CORRESPONDENCE_PATH.read_text(encoding="utf-8")) or {}
    theorems = data.get("theorems") or []
    ids = {item.get("id") for item in theorems if isinstance(item, dict)}
    return set(REQUIRED_CORRESPONDENCE_IDS).issubset(ids)

