# -*- coding: utf-8 -*-
"""可选 KaTeX 真解析闸（TeXPatch / pykatex 同一思路）。

启发式只能抓已知模式；KaTeX 才能回答「Typora 会不会爆红」。
本机有 Node + tools/katex_gate 时启用；没有则静默跳过。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
from collections import OrderedDict
from pathlib import Path

_GATE_DIR = Path(__file__).resolve().parents[2] / "tools" / "katex_gate"
_SCRIPT = _GATE_DIR / "validate.js"
_LOCK = threading.Lock()
_PROC: subprocess.Popen[str] | None = None
_DISABLED = False
_CACHE_MAX = 2048
_CACHE: OrderedDict[tuple[str, bool], tuple[bool | None, str]] = OrderedDict()


def katex_gate_available() -> bool:
    if os.environ.get("PDF2MD_KATEX_GATE", "").strip() in {"0", "off", "false", "no"}:
        return False
    if not _SCRIPT.is_file():
        return False
    if not (_GATE_DIR / "node_modules" / "katex").is_dir():
        return False
    return shutil.which("node") is not None


def reset_katex_engine() -> None:
    """测试用：关掉常驻进程并清空缓存。"""
    global _PROC, _DISABLED
    with _LOCK:
        if _PROC is not None:
            try:
                _PROC.stdin.close()
            except Exception:
                pass
            try:
                _PROC.terminate()
            except Exception:
                pass
            _PROC = None
        _DISABLED = False
        _CACHE.clear()


_WARMUP_TEX = r"\theta"


def warmup_katex() -> None:
    """后台拉起 Node，和下一步确定性修复重叠。

    katex_validate 对不含反斜杠的串会直接跳过，必须用带 \\ 的种子。
    """
    if not katex_gate_available():
        return

    def _run() -> None:
        try:
            katex_validate(_WARMUP_TEX)
        except Exception:
            pass

    threading.Thread(target=_run, name="katex-warmup", daemon=True).start()


def _creationflags() -> int:
    if sys.platform == "win32":
        return int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return 0


def _ensure_proc() -> subprocess.Popen[str] | None:
    global _PROC, _DISABLED
    if _DISABLED:
        return None
    if not katex_gate_available():
        _DISABLED = True
        return None
    if _PROC is not None and _PROC.poll() is None:
        return _PROC
    try:
        _PROC = subprocess.Popen(
            ["node", str(_SCRIPT)],
            cwd=str(_GATE_DIR),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            bufsize=1,
            creationflags=_creationflags(),
        )
    except OSError:
        _DISABLED = True
        _PROC = None
    return _PROC


def _cache_get(tex: str, display: bool) -> tuple[bool | None, str] | None:
    if len(tex) > 4000:
        return None
    key = (tex, display)
    hit = _CACHE.get(key)
    if hit is not None:
        _CACHE.move_to_end(key)
    return hit


def _cache_put(tex: str, display: bool, val: tuple[bool | None, str]) -> None:
    if len(tex) > 4000:
        return
    key = (tex, display)
    _CACHE[key] = val
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)


def _kill_proc(proc: subprocess.Popen[str] | None) -> None:
    global _PROC
    if proc is None:
        return
    try:
        proc.terminate()
    except Exception:
        pass
    _PROC = None


def _roundtrip(proc: subprocess.Popen[str], payload: str) -> dict | None:
    if proc.stdin is None or proc.stdout is None:
        return None
    proc.stdin.write(payload + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        return None
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def katex_validate(tex: str, *, display: bool = True) -> tuple[bool | None, str]:
    """返回 (ok, error)。ok 为 None 表示闸不可用，应回退启发式。"""
    body = (tex or "").strip()
    if not body:
        return True, ""
    if "\\" not in body:
        return True, ""
    hit = _cache_get(body, display)
    if hit is not None:
        return hit
    with _LOCK:
        hit = _cache_get(body, display)
        if hit is not None:
            return hit
        proc = _ensure_proc()
        if proc is None:
            return None, "unavailable"
        payload = json.dumps(
            {"id": 1, "tex": body, "display": display}, ensure_ascii=False
        )
        try:
            data = _roundtrip(proc, payload)
        except Exception as exc:
            _kill_proc(proc)
            return None, str(exc)
        if data is None:
            _kill_proc(proc)
            return None, "eof"
        result = (bool(data.get("ok")), str(data.get("error") or ""))
        _cache_put(body, display, result)
        return result


def katex_validate_many(
    texts: list[str], *, display: bool = True
) -> list[tuple[bool | None, str]]:
    """批量校验；命中缓存的不进 Node。"""
    if not texts:
        return []
    out: list[tuple[bool | None, str] | None] = [None] * len(texts)
    pending: list[tuple[int, str]] = []
    for i, raw in enumerate(texts):
        body = (raw or "").strip()
        if not body or "\\" not in body:
            out[i] = (True, "")
            continue
        hit = _cache_get(body, display)
        if hit is not None:
            out[i] = hit
        else:
            pending.append((i, body))
    if not pending:
        return [x or (True, "") for x in out]
    with _LOCK:
        still: list[tuple[int, str]] = []
        for i, body in pending:
            hit = _cache_get(body, display)
            if hit is not None:
                out[i] = hit
            else:
                still.append((i, body))
        if not still:
            return [x or (True, "") for x in out]
        proc = _ensure_proc()
        if proc is None:
            miss = (None, "unavailable")
            for i, _body in still:
                out[i] = miss
            return [x or miss for x in out]
        payload = json.dumps(
            {
                "batch": [
                    {"id": n, "tex": body, "display": display}
                    for n, (_i, body) in enumerate(still)
                ]
            },
            ensure_ascii=False,
        )
        try:
            data = _roundtrip(proc, payload)
        except Exception:
            _kill_proc(proc)
            miss = (None, "eof")
            for i, _body in still:
                out[i] = miss
            return [x or miss for x in out]
        rows = (data or {}).get("results") if data else None
        if not isinstance(rows, list) or len(rows) != len(still):
            miss = (None, "bad_reply")
            for i, _body in still:
                out[i] = miss
            return [x or miss for x in out]
        for (i, body), row in zip(still, rows):
            item = row if isinstance(row, dict) else {}
            result = (bool(item.get("ok")), str(item.get("error") or ""))
            _cache_put(body, display, result)
            out[i] = result
    return [x or (True, "") for x in out]
