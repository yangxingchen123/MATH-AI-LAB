"""stdlib OpenAI Chat Completions sidecar. No `openai` package. No Frozen Schema writes."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from .ai_prefs import load_prefs, models_for, save_prefs
from .credentials import (
    DEFAULT_BASE_URL,
    resolve_api_key,
    resolve_base_url,
    save_credentials,
)

DEFAULT_GPT_MODEL = "gpt-4.1"
PING_TIMEOUT = 20
CHAT_TIMEOUT = 90
Opener = Callable[..., Any]


def gpt_models() -> list[dict[str, str]]:
    rows = models_for("openai")
    return rows if rows else [{"id": DEFAULT_GPT_MODEL, "label": "GPT-4.1"}]


def _redact(text: str, api_key: str) -> str:
    if api_key and api_key in text:
        return text.replace(api_key, "sk-***")
    return text


def _parse_error(raw: bytes, status: int) -> str:
    text = raw.decode("utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        snippet = text.strip().replace("\n", " ")[:240]
        return f"GPT 返回 {status}" + (f"：{snippet}" if snippet else "")
    err = data.get("error") if isinstance(data, dict) else None
    if isinstance(err, dict) and err.get("message"):
        return f"GPT 返回 {status}：{err['message']}"
    if isinstance(err, str) and err.strip():
        return f"GPT 返回 {status}：{err.strip()}"
    return f"GPT 返回 {status}"


def _http(
    method: str,
    url: str,
    *,
    api_key: str,
    body: dict[str, Any] | None = None,
    timeout: int,
    opener: Opener | None,
) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("Content-Type", "application/json")
    request.add_header("User-Agent", "MATH-AI-LAB-gpt-sidecar")
    open_fn = opener or urllib.request.urlopen
    try:
        with open_fn(request, timeout=timeout) as response:
            raw = response.read()
            status = int(getattr(response, "status", 200) or 200)
    except urllib.error.HTTPError as exc:
        raw = exc.read() if exc.fp is not None else b""
        return {
            "ok": False,
            "error": _redact(_parse_error(raw, int(exc.code)), api_key),
            "status": int(exc.code),
        }
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        return {"ok": False, "error": _redact(f"无法连接 GPT：{reason}", api_key)}
    except TimeoutError:
        return {"ok": False, "error": "连接 GPT 超时"}
    except OSError as exc:
        return {"ok": False, "error": _redact(f"无法连接 GPT：{exc}", api_key)}
    if status >= 400:
        return {"ok": False, "error": _redact(_parse_error(raw, status), api_key), "status": status}
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return {"ok": False, "error": "GPT 返回了无法解析的内容"}
    return {"ok": True, "data": payload, "status": status}


def ping_gpt(
    *,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    opener: Opener | None = None,
) -> dict[str, Any]:
    key = (api_key or "").strip()
    if not key:
        return {"ok": False, "error": "缺少 GPT 密钥。请填写 OpenAI API Key。"}
    root_url = (base_url or DEFAULT_BASE_URL).strip().rstrip("/") or DEFAULT_BASE_URL
    result = _http("GET", f"{root_url}/models", api_key=key, timeout=PING_TIMEOUT, opener=opener)
    if not result.get("ok"):
        return result
    data = result.get("data")
    count = 0
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        count = len(data["data"])
    return {"ok": True, "error": "", "models": count}


def chat_gpt(
    *,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    base_url: str = DEFAULT_BASE_URL,
    opener: Opener | None = None,
) -> dict[str, Any]:
    key = (api_key or "").strip()
    if not key:
        return {"ok": False, "error": "缺少 GPT 密钥。请先接入 GPT。"}
    use_model = (model or "").strip() or DEFAULT_GPT_MODEL
    if not messages:
        return {"ok": False, "error": "没有可发送的对话内容"}
    root_url = base_url.strip().rstrip("/") if base_url.strip() else DEFAULT_BASE_URL
    result = _http(
        "POST",
        f"{root_url}/chat/completions",
        api_key=key,
        body={"model": use_model, "messages": messages, "temperature": 0.2},
        timeout=CHAT_TIMEOUT,
        opener=opener,
    )
    if not result.get("ok"):
        return result
    data = result.get("data")
    if not isinstance(data, dict):
        return {"ok": False, "error": "GPT 返回格式无法识别"}
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        return {"ok": False, "error": "GPT 没有返回内容"}
    first = choices[0] if isinstance(choices[0], dict) else {}
    message = first.get("message") if isinstance(first, dict) else {}
    content = message.get("content") if isinstance(message, dict) else ""
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or ""))
            else:
                parts.append(str(item))
        content = "".join(parts)
    text = str(content or "").strip()
    if not text:
        return {"ok": False, "error": "GPT 返回了空内容"}
    return {"ok": True, "error": "", "text": text, "model": use_model}


def gpt_status(root: Path) -> dict[str, Any]:
    prefs = load_prefs(root)
    key, source = resolve_api_key(root)
    model = prefs["model"] if prefs.get("provider") == "openai" else DEFAULT_GPT_MODEL
    if prefs.get("provider") == "openai" and not model:
        model = DEFAULT_GPT_MODEL
    return {
        "ok": True,
        "action": "status",
        "connected": bool(key),
        "has_key": bool(key),
        "key_source": source if key else "none",
        "provider": prefs.get("provider") or "",
        "model": model,
        "base_url": resolve_base_url(root),
    }


def connect_gpt(
    root: Path,
    *,
    model: str = DEFAULT_GPT_MODEL,
    api_key: str = "",
    base_url: str = "",
    opener: Opener | None = None,
) -> dict[str, Any]:
    allowed = {row["id"] for row in gpt_models()}
    use_model = (model or "").strip() or DEFAULT_GPT_MODEL
    if allowed and use_model not in allowed:
        use_model = next(iter(allowed))
    key, source = resolve_api_key(root, api_key)
    if not key:
        return {"ok": False, "error": "缺少 GPT 密钥。请填写 OpenAI API Key。"}
    use_base = resolve_base_url(root, base_url)
    ping = ping_gpt(api_key=key, base_url=use_base, opener=opener)
    if not ping.get("ok"):
        return ping
    if source == "input":
        save_credentials(root, {"api_key": key, "base_url": use_base})
    elif base_url.strip():
        save_credentials(root, {"base_url": use_base})
    save_prefs(root, {"provider": "openai", "model": use_model})
    return {
        "ok": True,
        "error": "",
        "action": "connect",
        "connected": True,
        "model": use_model,
        "base_url": use_base,
        "key_source": "file" if source == "input" else source,
        "models": ping.get("models", 0),
    }


def chat_from_root(
    root: Path,
    *,
    message: str,
    model: str = "",
    history: list[dict[str, str]] | None = None,
    opener: Opener | None = None,
) -> dict[str, Any]:
    text = (message or "").strip()
    if not text:
        return {"ok": False, "error": "请输入要发送给 GPT 的内容"}
    key, source = resolve_api_key(root)
    if not key:
        return {"ok": False, "error": "尚未接入 GPT：请先在设置里填写 API Key 并点接入。"}
    prefs = load_prefs(root)
    use_model = (model or "").strip()
    if not use_model:
        use_model = prefs["model"] if prefs.get("provider") == "openai" else DEFAULT_GPT_MODEL
    messages: list[dict[str, str]] = []
    for item in history or []:
        role = str(item.get("role") or "")
        content = str(item.get("content") or "")
        if role in {"user", "assistant", "system"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": text})
    result = chat_gpt(
        api_key=key,
        model=use_model,
        messages=messages,
        base_url=resolve_base_url(root),
        opener=opener,
    )
    if result.get("ok"):
        result["key_source"] = source
        result["action"] = "chat"
    return result


def dispatch(root: Path, payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"ok": False, "error": "请求必须是 JSON 对象"}
    action = str(payload.get("action") or "").strip()
    if action == "status":
        return gpt_status(root)
    if action == "connect":
        return connect_gpt(
            root,
            model=str(payload.get("model") or DEFAULT_GPT_MODEL),
            api_key=str(payload.get("api_key") or payload.get("apiKey") or ""),
            base_url=str(payload.get("base_url") or payload.get("baseUrl") or ""),
        )
    if action == "chat":
        history = payload.get("history")
        return chat_from_root(
            root,
            message=str(payload.get("message") or ""),
            model=str(payload.get("model") or ""),
            history=history if isinstance(history, list) else None,
        )
    return {"ok": False, "error": "未知操作。可用：status / connect / chat"}
