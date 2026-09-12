"""Local AI model preference. Not Frozen Schema. No API calls, no secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PREFS_DIRNAME = ".mathailab"
PREFS_FILENAME = "ai-model.json"
SECRET_KEYS = frozenset({"api_key", "apiKey", "token", "secret", "password"})

CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "cursor",
        "label": "Cursor",
        "models": (
            {"id": "auto", "label": "Auto"},
            {"id": "grok-4.6", "label": "Grok 4.6"},
            {"id": "composer-2", "label": "Composer"},
            {"id": "gpt-5.2", "label": "GPT-5.2"},
            {"id": "claude-4.6-sonnet", "label": "Claude Sonnet 4.6"},
            {"id": "claude-4.6-opus", "label": "Claude Opus 4.6"},
        ),
    },
    {
        "id": "openai",
        "label": "GPT（OpenAI）",
        "models": (
            {"id": "gpt-4.1", "label": "GPT-4.1"},
            {"id": "gpt-4o", "label": "GPT-4o"},
            {"id": "gpt-4o-mini", "label": "GPT-4o mini"},
            {"id": "gpt-5.2", "label": "GPT-5.2"},
            {"id": "o3", "label": "o3"},
        ),
    },
    {
        "id": "anthropic",
        "label": "Anthropic",
        "models": (
            {"id": "claude-opus-4.6", "label": "Claude Opus 4.6"},
            {"id": "claude-sonnet-4.6", "label": "Claude Sonnet 4.6"},
        ),
    },
    {
        "id": "xai",
        "label": "xAI",
        "models": (
            {"id": "grok-4.6", "label": "Grok 4.6"},
            {"id": "grok-4", "label": "Grok 4"},
        ),
    },
    {
        "id": "google",
        "label": "Google",
        "models": (
            {"id": "gemini-2.5-pro", "label": "Gemini 2.5 Pro"},
            {"id": "gemini-2.5-flash", "label": "Gemini 2.5 Flash"},
        ),
    },
    {
        "id": "ollama",
        "label": "本机 Ollama",
        "models": (
            {"id": "llama3.1", "label": "Llama 3.1"},
            {"id": "qwen2.5", "label": "Qwen 2.5"},
            {"id": "deepseek-r1", "label": "DeepSeek R1"},
        ),
    },
    {
        "id": "custom",
        "label": "自定义",
        "models": (),
    },
)

DEFAULT_PREFS: dict[str, str] = {
    "provider": "cursor",
    "model": "auto",
    "custom_model": "",
}


def providers() -> list[dict[str, Any]]:
    return [dict(row) for row in CATALOG]


def _provider(provider_id: str) -> dict[str, Any] | None:
    for row in CATALOG:
        if row["id"] == provider_id:
            return row
    return None


def models_for(provider_id: str) -> list[dict[str, str]]:
    row = _provider(provider_id)
    if row is None:
        return []
    return [dict(item) for item in row["models"]]


def flattened_choices() -> list[tuple[str, str, str]]:
    items: list[tuple[str, str, str]] = []
    for provider in CATALOG:
        if provider["id"] == "custom":
            items.append(("custom", "", f'{provider["label"]}…'))
            continue
        for model in provider["models"]:
            items.append(
                (
                    str(provider["id"]),
                    str(model["id"]),
                    f'{provider["label"]} · {model["label"]}',
                )
            )
    return items


def prefs_path(root: Path) -> Path:
    return Path(root) / PREFS_DIRNAME / PREFS_FILENAME


def _clean(raw: dict[str, Any] | None) -> dict[str, str]:
    data = dict(DEFAULT_PREFS)
    if not isinstance(raw, dict):
        return data
    provider = str(raw.get("provider") or "").strip()
    if _provider(provider) is None:
        return data
    data["provider"] = provider
    model = str(raw.get("model") or "").strip()
    custom = str(raw.get("custom_model") or "").strip()
    allowed = {item["id"] for item in models_for(provider)}
    if provider == "custom":
        data["model"] = ""
        data["custom_model"] = custom or model
        return data
    if model in allowed:
        data["model"] = model
    elif allowed:
        data["model"] = next(iter(allowed))
    data["custom_model"] = ""
    return data


def load_prefs(root: Path) -> dict[str, str]:
    path = prefs_path(root)
    if not path.is_file():
        return dict(DEFAULT_PREFS)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_PREFS)
    return _clean(payload if isinstance(payload, dict) else None)


def save_prefs(root: Path, payload: dict[str, Any]) -> dict[str, str]:
    cleaned = _clean(
        {
            key: value
            for key, value in dict(payload).items()
            if key not in SECRET_KEYS
        }
    )
    path = prefs_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return cleaned


def selection_label(prefs: dict[str, str]) -> str:
    provider = _provider(prefs.get("provider") or "")
    if provider is None:
        return "Cursor · Auto"
    if provider["id"] == "custom":
        name = (prefs.get("custom_model") or "").strip() or "未填写"
        return f'{provider["label"]} · {name}'
    model_id = prefs.get("model") or ""
    for item in provider["models"]:
        if item["id"] == model_id:
            return f'{provider["label"]} · {item["label"]}'
    return f'{provider["label"]} · {model_id or "Auto"}'
