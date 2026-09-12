"""Shared Lab → Exploration maps. Source: packages/domain-exploration/src/lab-map.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .constants import EXPLORATION_PKG

LAB_MAP_PATH = EXPLORATION_PKG / "src" / "lab-map.json"


@lru_cache(maxsize=1)
def load_lab_map() -> dict:
    data = json.loads(LAB_MAP_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("lab-map.json must be an object")
    return data


def lifecycle_state(status: str) -> str:
    raw = str(status or "").strip()
    mapped = (load_lab_map().get("lifecycle") or {}).get(raw)
    if mapped:
        return str(mapped)
    if raw.startswith("REJECTED"):
        return "rejected"
    return "exploring"


def pipeline_stage(status: str) -> str:
    raw = str(status or "").strip()
    mapped = (load_lab_map().get("pipeline") or {}).get(raw)
    if mapped:
        return str(mapped)
    return "exploration"


def maps_to_promotion() -> bool:
    return load_lab_map().get("never_maps_to_promotion") is not True
