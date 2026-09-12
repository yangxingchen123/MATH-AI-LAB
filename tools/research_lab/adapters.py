"""Unplugged external adapters. Never call a network, solver, or GPU."""

from __future__ import annotations

PLUGIN_STATUS: dict[str, str] = {
    "lean_specialist": "UNPLUGGED",
    "frontier_llm": "UNPLUGGED",
    "vector": "UNPLUGGED",
    "scheduler": "UNPLUGGED",
    "gpu_prover": "UNPLUGGED",
    "sat_smt": "UNPLUGGED",
    "mathlib": "none",
}


def invoke(name: str) -> dict:
    status = PLUGIN_STATUS.get(name, "UNKNOWN")
    return {
        "plugin": name,
        "status": status,
        "called": False,
        "usd": 0.0,
        "writes_source": False,
        "core_impact": False,
        "note": "Adapter is present as a socket. No API, GPU, SAT, or Mathlib call is made.",
    }


def all_unplugged() -> bool:
    return all(invoke(name)["called"] is False for name in PLUGIN_STATUS)


def may_expand_budget(layer: str, problem: dict) -> bool:
    if layer in {"C4", "C5"} and not problem.get("human_pi_signoff"):
        return False
    return layer in {"C0", "C1", "C2", "C3", "C4", "C5"}
