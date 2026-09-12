"""Local GPT credentials. Gitignored. Not Frozen Schema. Not Canonical Source."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .ai_prefs import PREFS_DIRNAME, SECRET_KEYS

CREDENTIALS_FILENAME = "credentials.json"
DEFAULT_BASE_URL = "https://api.openai.com/v1"


def credentials_path(root: Path) -> Path:
    return Path(root) / PREFS_DIRNAME / CREDENTIALS_FILENAME


def _clean_base_url(value: str) -> str:
    return value.strip().rstrip("/")


def load_credentials(root: Path) -> dict[str, Any]:
    path = credentials_path(root)
    data: dict[str, Any] = {
        "api_key": "",
        "base_url": DEFAULT_BASE_URL,
        "has_key": False,
    }
    if not path.is_file():
        return data
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return data
    if not isinstance(payload, dict):
        return data
    key = str(payload.get("api_key") or "").strip()
    base = _clean_base_url(str(payload.get("base_url") or ""))
    data["api_key"] = key
    data["base_url"] = base or DEFAULT_BASE_URL
    data["has_key"] = bool(key)
    return data


def save_credentials(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    existing = load_credentials(root)
    incoming = dict(payload or {})
    for secret in SECRET_KEYS:
        if secret in incoming and secret != "api_key":
            incoming.pop(secret, None)
    key = str(incoming.get("api_key") or "").strip()
    if not key:
        key = str(existing.get("api_key") or "").strip()
    base = _clean_base_url(str(incoming.get("base_url") or ""))
    if not base:
        base = str(existing.get("base_url") or DEFAULT_BASE_URL)
    cleaned = {"api_key": key, "base_url": base or DEFAULT_BASE_URL}
    path = credentials_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return {
        "api_key": key,
        "base_url": cleaned["base_url"],
        "has_key": bool(key),
    }


def resolve_api_key(root: Path, override: str = "") -> tuple[str, str]:
    typed = (override or "").strip()
    if typed:
        return typed, "input"
    stored = str(load_credentials(root).get("api_key") or "").strip()
    if stored:
        return stored, "file"
    env = str(os.environ.get("OPENAI_API_KEY") or "").strip()
    if env:
        return env, "env"
    return "", "none"


def resolve_base_url(root: Path, override: str = "") -> str:
    typed = _clean_base_url(override or "")
    if typed:
        return typed
    stored = _clean_base_url(str(load_credentials(root).get("base_url") or ""))
    if stored:
        return stored
    env = _clean_base_url(str(os.environ.get("OPENAI_BASE_URL") or ""))
    return env or DEFAULT_BASE_URL
