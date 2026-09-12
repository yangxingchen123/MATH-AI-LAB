from pathlib import Path
import json
import json

from tools.qt_workbench.credentials import load_credentials, save_credentials
from tools.qt_workbench.gpt_client import (
    DEFAULT_BASE_URL,
    chat_from_root,
    chat_gpt,
    connect_gpt,
    dispatch,
    gpt_status,
    ping_gpt,
)


class _FakeResponse:
    def __init__(self, payload: dict, status: int = 200) -> None:
        self.status = status
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_exc) -> bool:
        return False


def test_credentials_stay_out_of_model_prefs(tmp_path: Path):
    save_credentials(tmp_path, {"api_key": "sk-test-123", "base_url": DEFAULT_BASE_URL})
    loaded = load_credentials(tmp_path)
    assert loaded["api_key"] == "sk-test-123"
    assert loaded["has_key"] is True
    model_file = tmp_path / ".mathailab" / "ai-model.json"
    if model_file.is_file():
        assert "sk-test-123" not in model_file.read_text(encoding="utf-8")
    secret_file = tmp_path / ".mathailab" / "credentials.json"
    assert "sk-test-123" in secret_file.read_text(encoding="utf-8")


def test_ping_gpt_lists_models(tmp_path: Path):
    calls: list[str] = []

    def opener(request, timeout=0):
        calls.append(request.full_url)
        return _FakeResponse({"data": [{"id": "gpt-4.1"}]})

    result = ping_gpt(api_key="sk-test", base_url=DEFAULT_BASE_URL, opener=opener)
    assert result["ok"] is True
    assert "models" in calls[0]


def test_chat_gpt_reads_assistant_text():
    def opener(request, timeout=0):
        return _FakeResponse(
            {"choices": [{"message": {"role": "assistant", "content": "hello from gpt"}}]}
        )

    result = chat_gpt(
        api_key="sk-test",
        model="gpt-4.1",
        messages=[{"role": "user", "content": "hi"}],
        opener=opener,
    )
    assert result["ok"] is True
    assert result["text"] == "hello from gpt"


def test_connect_gpt_saves_openai_and_pings(tmp_path: Path):
    def opener(request, timeout=0):
        return _FakeResponse({"data": [{"id": "gpt-4.1"}]})

    result = connect_gpt(
        tmp_path,
        model="gpt-4.1",
        api_key="sk-live",
        opener=opener,
    )
    assert result["ok"] is True
    creds = load_credentials(tmp_path)
    assert creds["api_key"] == "sk-live"
    from tools.qt_workbench.ai_prefs import load_prefs

    prefs = load_prefs(tmp_path)
    assert prefs["provider"] == "openai"
    assert prefs["model"] == "gpt-4.1"


def test_ping_without_key_fails(tmp_path: Path):
    result = ping_gpt(api_key="", base_url=DEFAULT_BASE_URL)
    assert result["ok"] is False
    assert "密钥" in result["error"]


def test_status_does_not_leak_key(tmp_path: Path):
    save_credentials(tmp_path, {"api_key": "sk-secret-leak", "base_url": DEFAULT_BASE_URL})
    status = gpt_status(tmp_path)
    assert status["ok"] is True
    assert status["connected"] is True
    blob = json.dumps(status)
    assert "sk-secret-leak" not in blob
    assert status["key_source"] == "file"


def test_chat_from_root_uses_saved_key(tmp_path: Path):
    save_credentials(tmp_path, {"api_key": "sk-saved", "base_url": DEFAULT_BASE_URL})

    def opener(request, timeout=0):
        return _FakeResponse(
            {"choices": [{"message": {"role": "assistant", "content": "42"}}]}
        )

    result = chat_from_root(tmp_path, message="1+1?", model="gpt-4.1", opener=opener)
    assert result["ok"] is True
    assert result["text"] == "42"


def test_dispatch_unknown_action_fails(tmp_path: Path):
    result = dispatch(tmp_path, {"action": "shell"})
    assert result["ok"] is False


def test_gitignore_hides_local_secrets():
    text = Path(".gitignore").read_text(encoding="utf-8")
    assert ".mathailab/" in text
    assert ".env" in text
