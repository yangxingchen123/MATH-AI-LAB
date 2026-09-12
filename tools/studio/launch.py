"""Double-click launcher. Starts the read-only server if needed, then opens the browser."""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from collections.abc import Callable
from pathlib import Path
from typing import Any

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def studio_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/"


def is_serving(url: str, timeout: float = 0.4) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= int(response.status) < 400
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def start_detached(*, root: Path, host: str, port: int) -> None:
    command = [
        sys.executable,
        "-m",
        "tools.studio",
        "serve",
        "--host",
        host,
        "--port",
        str(port),
        "--root",
        str(root),
    ]
    kwargs: dict[str, Any] = {"cwd": str(root)}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(command, **kwargs)


def wait_until_up(url: str, *, attempts: int = 40, delay: float = 0.15) -> bool:
    for _ in range(attempts):
        if is_serving(url):
            return True
        time.sleep(delay)
    return False


def launch(
    *,
    root: Path,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    open_browser: bool = True,
    probe: Callable[[str], bool] | None = None,
    start: Callable[..., bool | None] | None = None,
    browse: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    url = studio_url(host, port)
    check = probe or is_serving
    spawn = start or (lambda **kwargs: start_detached(**kwargs) or wait_until_up(url))
    open_tab = browse or webbrowser.open
    if check(url):
        if open_browser:
            open_tab(url)
        return {"status": "already_running", "url": url, "writes": False}
    ok = spawn(root=root, host=host, port=port)
    if ok is False:
        return {"status": "failed", "url": url, "writes": False}
    if open_browser:
        open_tab(url)
    return {"status": "started", "url": url, "writes": False}
