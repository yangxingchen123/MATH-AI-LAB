"""Local stdlib server. Binds loopback by default."""

from __future__ import annotations

from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .app import handle_request


def serve(*, root: Path, host: str, port: int) -> None:
    handler = partial(StudioHandler, root=root)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"MATH-AI-LAB studio  http://{host}:{port}/  （只读）", flush=True)
    print("关闭本窗口即停止界面。", flush=True)
    server.serve_forever()


class StudioHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, root: Path, **kwargs) -> None:
        self._root = root
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self._dispatch("GET")

    def do_HEAD(self) -> None:
        self._dispatch("HEAD")

    def do_POST(self) -> None:
        self._dispatch("POST")

    def do_PUT(self) -> None:
        self._dispatch("PUT")

    def do_DELETE(self) -> None:
        self._dispatch("DELETE")

    def _dispatch(self, method: str) -> None:
        parsed = urlparse(self.path)
        query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
        response = handle_request(method, parsed.path, query, root=self._root)
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Cache-Control", "no-store")
        if method == "HEAD":
            self.send_header("Content-Length", str(len(response.body)))
            self.end_headers()
            return
        self.send_header("Content-Length", str(len(response.body)))
        self.end_headers()
        self.wfile.write(response.body)

    def log_message(self, format: str, *args) -> None:
        return
