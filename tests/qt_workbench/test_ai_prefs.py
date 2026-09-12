from pathlib import Path
import json

from tools.qt_workbench.ai_prefs import (
    DEFAULT_PREFS,
    flattened_choices,
    load_prefs,
    models_for,
    providers,
    save_prefs,
    selection_label,
)


def test_catalog_has_selectable_providers_and_models():
    ids = [row["id"] for row in providers()]
    assert "cursor" in ids
    assert "openai" in ids
    assert any(row["id"] == "gpt-4.1" for row in models_for("openai"))
    assert any(row["id"] == "gpt-4o" for row in models_for("openai"))
    assert "anthropic" in ids
    assert "xai" in ids
    assert "ollama" in ids
    assert "custom" in ids
    cursor_models = [row["id"] for row in models_for("cursor")]
    assert "auto" in cursor_models
    assert flattened_choices()
    assert any(item[0] == "cursor" and item[1] == "auto" for item in flattened_choices())


def test_save_and_load_roundtrip(tmp_path: Path):
    payload = save_prefs(tmp_path, {"provider": "xai", "model": "grok-4.6"})
    loaded = load_prefs(tmp_path)
    assert payload["provider"] == "xai"
    assert loaded["model"] == "grok-4.6"
    assert "api_key" not in loaded
    stored = (tmp_path / ".mathailab" / "ai-model.json").read_text(encoding="utf-8")
    assert "grok-4.6" in stored
    assert "sk-" not in stored


def test_unknown_provider_falls_back_to_default(tmp_path: Path):
    (tmp_path / ".mathailab").mkdir()
    (tmp_path / ".mathailab" / "ai-model.json").write_text(
        '{"provider": "nope", "model": "x"}',
        encoding="utf-8",
    )
    loaded = load_prefs(tmp_path)
    assert loaded["provider"] == DEFAULT_PREFS["provider"]
    assert loaded["model"] == DEFAULT_PREFS["model"]


def test_custom_model_is_kept(tmp_path: Path):
    save_prefs(tmp_path, {"provider": "custom", "model": "", "custom_model": "my-local-70b"})
    loaded = load_prefs(tmp_path)
    assert loaded["provider"] == "custom"
    assert loaded["custom_model"] == "my-local-70b"
    assert "my-local-70b" in selection_label(loaded)


def test_save_strips_secrets(tmp_path: Path):
    save_prefs(
        tmp_path,
        {
            "provider": "openai",
            "model": "gpt-4.1",
            "api_key": "sk-secret",
            "apiKey": "sk-secret",
        },
    )
    stored = (tmp_path / ".mathailab" / "ai-model.json").read_text(encoding="utf-8")
    assert "sk-secret" not in stored
    assert "api_key" not in stored


def test_cli_gpt_status_without_key(tmp_path: Path, capsys):
    from tools.qt_workbench.cli import main

    assert main(["--root", str(tmp_path), "gpt-status"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["connected"] is False
    assert "api_key" not in payload

